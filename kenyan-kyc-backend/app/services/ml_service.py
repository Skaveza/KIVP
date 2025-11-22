import re
import os
import logging
from datetime import datetime
from typing import Dict, Optional
from functools import lru_cache

import torch
from PIL import Image, UnidentifiedImageError
from transformers import AutoProcessor, AutoModelForTokenClassification

logger = logging.getLogger(__name__)


def _resolve_default_model_path() -> str:
    """
    Pick a default path that works in both:
    - local dev repo (./app/models/...)
    - docker runtime (/app/models/...)
    """
    candidates = [
        os.path.abspath("app/models/layoutlmv3_receipt_model/checkpoint-1000"),
        "/app/models/layoutlmv3_receipt_model/checkpoint-1000",
    ]
    for p in candidates:
        if os.path.isdir(p):
            return p
    # fallback to first candidate even if missing (we'll error later with a clear msg)
    return candidates[0]


class KYCModelService:
    """
    Service for running LayoutLMv3-based KYC receipt extraction.
    Lazily loaded via get_ml_service() to avoid startup crashes in Docker/Render.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        local_files_only: Optional[bool] = None,
    ):
        env_model_path = model_path or os.getenv("MODEL_PATH")
        if env_model_path:
            self.model_path = os.path.abspath(env_model_path)
        else:
            self.model_path = _resolve_default_model_path()

        env_device = device or os.getenv("MODEL_DEVICE", "cpu")
        self.device = torch.device(env_device)

        # default True to preserve your current behavior
        if local_files_only is None:
            self.local_files_only = (
                os.getenv("LOCAL_FILES_ONLY", "true").lower() == "true"
            )
        else:
            self.local_files_only = bool(local_files_only)

        self._load_model()

    def _load_model(self):
        if not os.path.isdir(self.model_path):
            raise RuntimeError(
                f"Model path not found: {self.model_path}. "
                f"Make sure MODEL_PATH is set and the model is downloaded/mounted "
                f"before running inference."
            )

        logger.info("Loading KYC model from %s on device %s", self.model_path, self.device)

        # Load processor (image processor + tokenizer)
        self.processor = AutoProcessor.from_pretrained(
            self.model_path,
            local_files_only=self.local_files_only,
        )

        # Ensure OCR is enabled so features["words"] exists
        if hasattr(self.processor, "image_processor") and hasattr(
            self.processor.image_processor, "apply_ocr"
        ):
            self.processor.image_processor.apply_ocr = True

        # Load model
        self.model = AutoModelForTokenClassification.from_pretrained(
            self.model_path,
            local_files_only=self.local_files_only,
        ).to(self.device)

        self.model.eval()

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
    # Confidence extraction from logits
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
    # Auto currency detection
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
    # Decode extracted fields from BIO labels
    # ---------------------------------------------------------------------
    def decode_predictions(self, tokens, labels) -> Dict:
        field_tokens = {
            "company": [],
            "date": [],
            "address": [],
            "total": [],
        }

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
    # Main prediction entrypoint
    # ---------------------------------------------------------------------
    def predict(self, image_path: str) -> Dict:
        # Guard for pdfs (since your backend allows pdf uploads)
        _, ext = os.path.splitext(image_path.lower())
        if ext == ".pdf":
            raise ValueError(
                "PDF receipts are not supported by the current ML pipeline. "
                "Convert PDF to an image before inference, or add a PDF->image step."
            )

        try:
            image = Image.open(image_path).convert("RGB")
        except UnidentifiedImageError as e:
            raise ValueError(f"Unsupported image format for {image_path}") from e

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
        filtered_tokens = []
        filtered_labels = []
        filtered_token_ids = []

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
        parsed_total = (
            self.parse_amount(extracted.get("total", ""))
            or self.parse_total_from_text(raw_text)
        )

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

    def run_inference(self, image_path: str) -> Dict:
        return self.predict(image_path)


# ---------------------------------------------------------------------
# Lazy singleton loader (safe for Render/Oracle cold starts)
# ---------------------------------------------------------------------
@lru_cache()
def get_ml_service() -> KYCModelService:
    return KYCModelService()


# Backward-compatible lazy proxy:

class _LazyServiceProxy:
    def __getattr__(self, name):
        return getattr(get_ml_service(), name)


ml_service = _LazyServiceProxy()


def predict_receipt(image_path: str) -> Dict:
    return get_ml_service().predict(image_path)
