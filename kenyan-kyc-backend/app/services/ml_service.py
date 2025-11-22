import re
import os
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForTokenClassification
from huggingface_hub import snapshot_download

from ..core.config import settings

logger = logging.getLogger(__name__)
_init_lock = threading.Lock()


class KYCModelService:
    """
    Production-safe LayoutLMv3 receipt extraction:
    - Lazy loads model on first use (better for Render/Oracle)
    - Can optionally download model if missing
    """

    def __init__(self):
        self._loaded = False
        self.model_path: Optional[Path] = None
        self.device: Optional[torch.device] = None
        self.processor = None
        self.model = None

        # Label mappings
        self.label_list = [
            "O",
            "B-company", "I-company",
            "B-date", "I-date",
            "B-address", "I-address",
            "B-total", "I-total",
        ]
        self.id2label = {i: label for i, label in enumerate(self.label_list)}

    # ---------------------------------------------------------------------
    # Model path resolution + optional download
    # ---------------------------------------------------------------------
    def _resolve_model_path(self) -> Path:
        """
        Accepts either:
        - MODEL_PATH pointing directly to checkpoint dir
        - MODEL_PATH pointing to model root dir (contains checkpoint-*)
        """
        env_path = os.getenv("MODEL_PATH") or settings.MODEL_PATH
        p = Path(env_path).expanduser().resolve()

        # If it's a root folder, try to find checkpoint inside
        if p.exists() and p.is_dir():
            # If it already looks like a checkpoint folder, use it
            if (p / "config.json").exists() or p.name.startswith("checkpoint-"):
                return p

            # Otherwise find newest checkpoint-* under root
            ckpts = sorted(p.glob("checkpoint-*"))
            if ckpts:
                return ckpts[-1]

        return p  # may not exist yet

    def _maybe_download_model(self, target_path: Path) -> Path:
        """
        If model isn't available locally, optionally download from HF.
        Requires env vars:
          HF_MODEL_REPO=your-org/your-model
          (optional) HF_MODEL_REVISION=main
          ALLOW_MODEL_DOWNLOAD=true
        """
        allow = os.getenv("ALLOW_MODEL_DOWNLOAD", "false").lower() in ("1", "true", "yes")
        repo_id = os.getenv("HF_MODEL_REPO")
        revision = os.getenv("HF_MODEL_REVISION")

        if not allow or not repo_id:
            return target_path

        logger.info("Model not found at %s. Downloading from HF repo %s ...", target_path, repo_id)

        # Download snapshot into a stable local dir
        local_root = target_path.parent if target_path.suffix == "" else Path("/app/models")
        local_root.mkdir(parents=True, exist_ok=True)

        snapshot_download(
            repo_id=repo_id,
            revision=revision,
            local_dir=str(local_root),
            local_dir_use_symlinks=False,
        )

        # Re-resolve after download
        resolved = self._resolve_model_path()
        logger.info("Downloaded model resolved to %s", resolved)
        return resolved

    def load(self):
        """
        Lazy model load with a lock (safe for concurrent requests).
        """
        if self._loaded:
            return

        with _init_lock:
            if self._loaded:
                return

            path = self._resolve_model_path()
            if not path.exists():
                path = self._maybe_download_model(path)

            if not path.exists():
                raise RuntimeError(
                    f"Model path not found: {path}. "
                    "Either bake the model into the container or set "
                    "HF_MODEL_REPO + ALLOW_MODEL_DOWNLOAD=true."
                )

            self.model_path = path
            self.device = torch.device(os.getenv("MODEL_DEVICE", "cpu"))

            # Optional: cap threads for tiny cloud CPUs
            try:
                torch.set_num_threads(int(os.getenv("TORCH_NUM_THREADS", "1")))
            except Exception:
                pass

            logger.info("Loading processor from %s on %s", self.model_path, self.device)

            self.processor = AutoProcessor.from_pretrained(
                str(self.model_path),
                local_files_only=True,
            )

            # Ensure OCR is enabled
            if hasattr(self.processor, "image_processor") and hasattr(
                self.processor.image_processor, "apply_ocr"
            ):
                self.processor.image_processor.apply_ocr = True

            logger.info("Loading model from %s on %s", self.model_path, self.device)

            self.model = AutoModelForTokenClassification.from_pretrained(
                str(self.model_path),
                local_files_only=True,
            ).to(self.device)

            self.model.eval()
            self._loaded = True
            logger.info("Model loaded successfully.")

    # ---------------------------------------------------------------------
    # Confidence extraction
    # ---------------------------------------------------------------------
    def get_confidence_scores(self, logits: torch.Tensor, predictions, token_ids):
        scores = []
        softmax = torch.nn.functional.softmax(logits, dim=-1)
        special_ids = set(self.processor.tokenizer.all_special_ids)

        for i, tok_id in enumerate(token_ids):
            if tok_id in special_ids:
                continue
            scores.append(float(softmax[i][predictions[i]].cpu().item()))

        return scores

    # ---------------------------------------------------------------------
    # Date parsing
    # ---------------------------------------------------------------------
    def parse_date(self, text: str):
        if not text:
            return None

        text_no_spaces = text.replace(" ", "")
        patterns = [
            r"\d{4}-\d{2}-\d{2}",
            r"\d{2}/\d{2}/\d{4}",
            r"\d{2}-\d{2}-\d{4}",
            r"\d{1,2}/\d{1,2}/\d{2,4}",
        ]

        for p in patterns:
            match = re.search(p, text_no_spaces)
            if not match:
                continue

            candidate = match.group()
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(candidate, fmt).date()
                except ValueError:
                    continue

        return None

    # ---------------------------------------------------------------------
    # Amount parsing
    # ---------------------------------------------------------------------
    def parse_amount(self, value: str):
        if not value:
            return None

        value = (
            value.replace(",", "")
                 .replace("KES", "")
                 .replace("KSH", "")
                 .replace("KSh", "")
                 .strip()
        )

        match = re.search(r"\d+(?:\.\d{1,2})?", value)
        return float(match.group()) if match else None

    def parse_total_from_text(self, text: str):
        if not text:
            return None

        cleaned = (
            text.replace("KES", "")
                .replace("KSH", "")
                .replace("KSh", "")
                .replace(",", "")
        )

        matches = re.findall(r"\d+(?:\.\d{1,2})?", cleaned)
        if not matches:
            return None

        amounts = []
        for m in matches:
            try:
                value = float(m)
                if value < 10_000_000:
                    amounts.append(value)
            except ValueError:
                continue

        return max(amounts) if amounts else None

    # ---------------------------------------------------------------------
    # Currency detection
    # ---------------------------------------------------------------------
    def detect_currency(self, raw_text: str):
        if any(x in raw_text for x in ["KES", "KSH", "KSh"]):
            return "KES"
        if "$" in raw_text:
            return "USD"
        if "€" in raw_text:
            return "EUR"
        if "£" in raw_text:
            return "GBP"
        return "KES"

    # ---------------------------------------------------------------------
    # Decode BIO predictions
    # ---------------------------------------------------------------------
    def decode_predictions(self, tokens, labels) -> Dict:
        field_tokens = {"company": [], "date": [], "address": [], "total": []}
        current_field = None
        buffer = []

        def flush():
            nonlocal buffer, current_field
            if current_field and buffer:
                field_tokens[current_field].extend(buffer)
            buffer = []
            current_field = None

        for tok, lbl in zip(tokens, labels):
            if lbl == "O":
                flush()
                continue

            prefix, fld = lbl.split("-", 1)
            if prefix == "B":
                flush()
                current_field = fld
                buffer = [tok]
            elif prefix == "I" and current_field == fld:
                buffer.append(tok)
            else:
                flush()
                current_field = fld
                buffer = [tok]

        flush()

        fields = {}
        for key, toks in field_tokens.items():
            if toks:
                text = self.processor.tokenizer.convert_tokens_to_string(toks).strip()
            else:
                text = ""
            fields[key] = text

        return fields

    # ---------------------------------------------------------------------
    # Main prediction
    # ---------------------------------------------------------------------
    def predict(self, image_path: str) -> Dict:
        self.load()  # lazy init here

        image = Image.open(image_path).convert("RGB")
        encoding = self.processor(images=image, return_tensors="pt")

        input_ids = encoding["input_ids"][0]
        token_ids = input_ids.tolist()
        tokens = self.processor.tokenizer.convert_ids_to_tokens(token_ids)

        encoding = {k: v.to(self.device) for k, v in encoding.items()}

        with torch.no_grad():
            outputs = self.model(**encoding)
            logits = outputs.logits[0]
            predictions = logits.argmax(-1).tolist()

        special_ids = set(self.processor.tokenizer.all_special_ids)
        filtered_tokens, filtered_labels, filtered_token_ids = [], [], []

        for tok_id, tok, pred in zip(token_ids, tokens, predictions):
            if tok_id in special_ids:
                continue
            filtered_tokens.append(tok)
            filtered_labels.append(self.id2label[pred])
            filtered_token_ids.append(tok_id)

        extracted = self.decode_predictions(filtered_tokens, filtered_labels)

        confidence_scores = self.get_confidence_scores(logits, predictions, token_ids)
        avg_conf = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        raw_text = self.processor.tokenizer.convert_tokens_to_string(filtered_tokens)

        parsed_date = self.parse_date(extracted.get("date", "")) or self.parse_date(raw_text)
        parsed_total = self.parse_amount(extracted.get("total", "")) or self.parse_total_from_text(raw_text)
        detected_currency = self.detect_currency(raw_text)

        return {
            "company_name": extracted["company"],
            "receipt_date": parsed_date,
            "receipt_address": extracted["address"],
            "total_amount": parsed_total,
            "currency": detected_currency,
            "confidence": avg_conf,
            "raw_tokens": filtered_tokens,
            "raw_labels": filtered_labels,
            "raw_text": raw_text,
        }

    # Backward compatible wrapper
    def run_inference(self, image_path: str) -> Dict:
        return self.predict(image_path)


# Global lazy instance
ml_service = KYCModelService()


def predict_receipt(image_path: str) -> Dict:
    return ml_service.predict(image_path)
