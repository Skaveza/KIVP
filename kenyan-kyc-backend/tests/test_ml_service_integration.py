from pathlib import Path
from datetime import date

from app.services.ml_service import ml_service


def test_ml_service_extracts_key_fields():
    # Use a path relative to this test file
    img_path = Path(__file__).with_name("test_receipt.jpg")
    assert img_path.exists(), f"Test image not found at {img_path}"

    res = ml_service.run_inference(str(img_path))

    # Basic structure checks
    assert isinstance(res, dict)
    assert "raw_text" in res and res["raw_text"]
    assert "confidence" in res and res["confidence"] > 0.0

    # Date should be parsed (using the fallback from raw_text)
    assert res["receipt_date"] is not None
    assert isinstance(res["receipt_date"], date)

    # Total amount should be parsed and positive
    assert res["total_amount"] is not None
    assert isinstance(res["total_amount"], (int, float))
    assert res["total_amount"] > 0

    # Currency should be KES for this sample
    assert res["currency"] == "KES"

    # Address should at least be a string (even if imperfect)
    assert isinstance(res["receipt_address"], str)
