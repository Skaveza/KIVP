# app/api/routes/receipts.py  (or app/routes/receipts.py)

from datetime import datetime
import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.models import User, Receipt
from app.schemas import ReceiptResponse
from app.api.dependencies import get_current_user
from app.services.ml_service import ml_service
from app.services.kyc_scoring import KYCScorer

router = APIRouter(prefix="/receipts", tags=["Receipts"])

# ./uploads/receipts (from your .env UPLOAD_DIR)
UPLOAD_DIR = os.path.join(settings.UPLOAD_DIR, "receipts")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("", response_model=list[ReceiptResponse])
def list_receipts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List the current user's receipts (most recent first).
    Used by:
      - ReceiptList
      - SpendingCharts
    """
    receipts = (
        db.query(Receipt)
        .filter(Receipt.user_id == current_user.id)
        .order_by(Receipt.uploaded_at.desc())
        .limit(50)
        .all()
    )
    return receipts


@router.post("/upload", response_model=ReceiptResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload receipt → run OCR/ML → save result → return parsed structured fields.
    Also triggers KYC scoring for the current user.
    """

    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded",
        )

    # Generate unique filename
    receipt_id = uuid4()
    original_name = file.filename or "receipt"
    _, ext = os.path.splitext(original_name)
    safe_name = f"{receipt_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create DB entry in 'processing' state
    receipt = Receipt(
        id=receipt_id,              # UUID object, fine for Postgres UUID
        user_id=current_user.id,    # ✅ from JWT
        file_name=original_name,
        file_path=file_path,
        status="processing",
        uploaded_at=datetime.utcnow(),
    )

    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    # Run ML
    try:
        parsed = ml_service.run_inference(file_path) or {}

        receipt.company_name = parsed.get("company_name")
        receipt.receipt_date = parsed.get("receipt_date")
        receipt.receipt_address = parsed.get("receipt_address")
        receipt.total_amount = parsed.get("total_amount")
        receipt.currency = parsed.get("currency", "KES")

        confidence = parsed.get("confidence") or 0.0
        receipt.overall_confidence = confidence
        receipt.confidence_company = confidence
        receipt.confidence_date = confidence
        receipt.confidence_address = confidence
        receipt.confidence_total = confidence

        if hasattr(receipt, "raw_extraction_json"):
            receipt.raw_extraction_json = parsed

        receipt.status = "completed"
        if hasattr(receipt, "processing_completed_at"):
            receipt.processing_completed_at = datetime.utcnow()

    except Exception as e:
        receipt.status = "failed"
        receipt.error_message = str(e)

    db.commit()
    db.refresh(receipt)

    # 🔁 Recalculate KYC score for this user after each (successful) upload
    try:
        scorer = KYCScorer(db)
        scorer.calculate_user_score(str(current_user.id))
        db.commit()  # harmless even if KYCScorer already committed internally
    except Exception as e:
        # Don't break the upload if scoring fails – just log it in dev
        print("Error recalculating KYC score:", e)

    return receipt
