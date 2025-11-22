import re
import os 
from datetime import datetime
from typing import Dict

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForTokenClassification

from ..core.config import settings


class KYCModelService:
    """
    Service for running LayoutLMv3-based KYC receipt extraction.
    """

    def __init__(self):
        self.model_path = os.path.abspath(os.getenv("MODEL_PATH", "app/models/layoutlmv3_receipt_model/checkpoint-1000"))
        self.device = torch.device(os.getenv("MODEL_DEVICE", "cpu"))


        # Load processor (image processor + tokenizer)
        self.processor = AutoProcessor.from_pretrained(
            self.model_path,
            local_files_only=True,
        )

        # Ensure OCR is enabled so features["words"] exists
        if hasattr(self.processor, "image_processor") and hasattr(
            self.processor.image_processor, "apply_ocr"
        ):
            self.processor.image_processor.apply_ocr = True

        # Load model
        self.model = AutoModelForTokenClassification.from_pretrained(
            self.model_path,
            local_files_only=True,
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
        """
        Compute per-token confidence scores (excluding special tokens).

        logits: (seq_len, num_labels)
        predictions: list[int] length seq_len
        token_ids: list[int] length seq_len
        """
        scores = []
        softmax = torch.nn.functional.softmax(logits, dim=-1)
        special_ids = set(self.processor.tokenizer.all_special_ids)

        for i, tok_id in enumerate(token_ids):
            if tok_id in special_ids:
                continue
            scores.append(float(softmax[i][predictions[i]].cpu().item()))

        return scores

    # ---------------------------------------------------------------------
    # Date parsing with multiple formats + fallback
    # ---------------------------------------------------------------------
    def parse_date(self, text: str):
        """
        Try to parse a date from the given text.
        Supports formats like:
        - 2015-11-27
        - 27/11/2015
        - 11/27/2015
        - 27-11-2015
        """
        if not text:
            return None

        # Remove spaces to make "27 - 11 - 2015" -> "27-11-2015"
        text_no_spaces = text.replace(" ", "")

        patterns = [
            r"\d{4}-\d{2}-\d{2}",  # 2015-11-27
            r"\d{2}/\d{2}/\d{4}",  # 27/11/2015 or 11/27/2015
            r"\d{2}-\d{2}-\d{4}",  # 27-11-2015
            r"\d{1,2}/\d{1,2}/\d{2,4}",
        ]

        for p in patterns:
            match = re.search(p, text_no_spaces)
            if not match:
                continue

            candidate = match.group()

            # Try several formats
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(candidate, fmt).date()
                except ValueError:
                    continue

        return None

    # ---------------------------------------------------------------------
    # Amount parsing (for already-extracted field snippet)
    # ---------------------------------------------------------------------
    def parse_amount(self, value: str):
        """
        Extract a single numeric value from a short snippet (e.g. the 'total' field).
        """
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

    # ---------------------------------------------------------------------
    # Heuristic: pick the most likely total from the entire receipt text
    # ---------------------------------------------------------------------
    def parse_total_from_text(self, text: str):
        """
        Scan the full receipt text and pick a likely total amount.
        Simple heuristic:
        - Find all numeric values like 499.88, 85.00, etc.
        - Filter out obviously huge numbers (likely IDs)
        - Return the largest remaining value
        """
        if not text:
            return None

        cleaned = (
            text.replace("KES", "")
                .replace("KSH", "")
                .replace("KSh", "")
                .replace(",", "")
        )

        # Find ALL numbers like 499.88, 85.00, 15080615, etc.
        matches = re.findall(r"\d+(?:\.\d{1,2})?", cleaned)
        if not matches:
            return None

        amounts = []
        for m in matches:
            try:
                value = float(m)
                # simple sanity filter: ignore very large values (likely IDs)
                if value < 10_000_000:
                    amounts.append(value)
            except ValueError:
                continue

        if not amounts:
            return None

        # Heuristic: pick the largest amount as total
        return max(amounts)

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
        # default to Kenya
        return "KES"

    # ---------------------------------------------------------------------
    # Decode extracted fields from BIO labels
    # ---------------------------------------------------------------------
    def decode_predictions(self, tokens, labels) -> Dict:
        """
        Group subword tokens into fields using BIO labels, then detokenize
        with the tokenizer to get readable text per field.
        """
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
                # Inconsistent I- tag → treat as new field
                flush()
                current_field = fld
                buffer = [tok]

        flush()

        # Detokenize per field
        fields = {}
        for key, toks in field_tokens.items():
            if toks:
                text = self.processor.tokenizer.convert_tokens_to_string(toks)
                text = text.strip()
            else:
                text = ""
            fields[key] = text

        return fields

    # ---------------------------------------------------------------------
    # Main prediction entrypoint
    # ---------------------------------------------------------------------
    def predict(self, image_path: str) -> Dict:
        """
        Run OCR + LayoutLMv3 token classification on a receipt image and
        return structured fields + raw debug info.
        """
        image = Image.open(image_path).convert("RGB")

        # Processor does OCR + tokenization
        encoding = self.processor(images=image, return_tensors="pt")
        input_ids = encoding["input_ids"][0]  # (seq_len,)
        token_ids = input_ids.tolist()
        tokens = self.processor.tokenizer.convert_ids_to_tokens(token_ids)

        # Move to device
        encoding = {k: v.to(self.device) for k, v in encoding.items()}

        with torch.no_grad():
            outputs = self.model(**encoding)
            # logits: (1, seq_len, num_labels)
            logits = outputs.logits[0]  # (seq_len, num_labels)
            predictions = logits.argmax(-1).tolist()  # list[int] length seq_len

        # Filter out special tokens, keep tokens + labels aligned
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

        # Decode fields from BIO labels
        extracted = self.decode_predictions(filtered_tokens, filtered_labels)

        # Confidence across non-special tokens
        confidence_scores = self.get_confidence_scores(logits, predictions, token_ids)
        avg_conf = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        # Build clean raw text
        raw_text = self.processor.tokenizer.convert_tokens_to_string(filtered_tokens)

        # Final post-processed values
        # 1) Try to parse from the extracted field
        # 2) If that fails, fall back to scanning full raw_text
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

    # ---------------------------------------------------------------------
    # Compatibility wrapper used by routes/tests
    # ---------------------------------------------------------------------
    def run_inference(self, image_path: str) -> Dict:
        """
        Wrapper so existing code that calls `ml_service.run_inference(...)`
        keeps working.
        """
        return self.predict(image_path)


# Global instance used across the app
ml_service = KYCModelService()


def predict_receipt(image_path: str) -> Dict:
    """
    Optional function-level API for convenience.
    """
    return ml_service.predict(image_path)
