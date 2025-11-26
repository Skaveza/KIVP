import os
import shutil
from uuid import uuid4, UUID
from fastapi import Security
from datetime import datetime, date
from decimal import Decimal
import logging

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.models import User, Receipt
from app.schemas import ReceiptResponse
from app.api.dependencies import get_current_user
from app.services.ml_service import ml_service
from app.services.kyc_scoring import KYCScorer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/receipts", tags=["Receipts"])

UPLOAD_DIR = os.path.join(settings.UPLOAD_DIR, "receipts")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def to_primitive(obj):
    """Recursively convert dates/decimals/etc. into JSON-safe types."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, dict):
        return {k: to_primitive(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_primitive(v) for v in obj]

    return obj


def extract_company_name(parsed: dict) -> str | None:
    """
    Try multiple keys / structures to find a merchant/company name
    from the ML output. This helps when the model changes keys
    or returns a 'fields' array instead of flat keys.
    """
    if not isinstance(parsed, dict):
        return None

    # 1) Direct keys that might exist
    for key in ["company_name", "merchant_name", "store_name", "business_name"]:
        val = parsed.get(key)
        if val:
            return str(val).strip()

    # 2) Generic "fields" style outputs
    fields = parsed.get("fields")
    if isinstance(fields, list):
        for field in fields:
            label = str(field.get("label", "")).lower()
            if label in {
                "merchant",
                "merchant name",
                "company",
                "business",
                "store",
                "shop name",
            }:
                val = field.get("value") or field.get("text")
                if val:
                    return str(val).strip()

    return None


@router.get("", response_model=list[ReceiptResponse])
def list_receipts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List the current user's receipts (most recent first).
    Used by dashboard + analytics.
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
    Upload receipt -> run OCR/ML -> save result -> return parsed structured fields.
    Also triggers KYC scoring for the current user.
    """
    print("=" * 80, flush=True)
    print("UPLOAD STARTED", flush=True)
    print(f"User ID: {current_user.id}", flush=True)
    print(f"User Email: {current_user.email}", flush=True)
    print(f"Filename: {file.filename}", flush=True)
    print(f"Content Type: {file.content_type}", flush=True)
    print("=" * 80, flush=True)
    
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

    print(f"Saving file to: {file_path}", flush=True)

    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_size = os.path.getsize(file_path)
        print(f"File saved successfully ({file_size} bytes)", flush=True)
    except Exception as e:
        print(f"FAILED to save file: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )

    # Create DB entry in 'processing' state
    print("Creating receipt record in database...", flush=True)
    receipt = Receipt(
        id=receipt_id,
        user_id=current_user.id,
        file_name=original_name,
        file_path=file_path,
        file_size=file_size if hasattr(Receipt, "file_size") else None,
        file_type=file.content_type if hasattr(Receipt, "file_type") else None,
        status="processing",
        uploaded_at=datetime.utcnow(),
        processing_started_at=datetime.utcnow()
        if hasattr(Receipt, "processing_started_at")
        else None,
    )

    try:
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        print(f"Receipt record created: {receipt_id}", flush=True)
    except Exception as e:
        print(f"FAILED to create receipt record: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise

    # Run ML
    print("Starting ML inference...", flush=True)
    print(f"ML Service object: {ml_service}", flush=True)
    print(f"ML Service loaded: {ml_service._loaded}", flush=True)
    print(f"Model path: {settings.MODEL_PATH}", flush=True)
    print(f"Model path exists: {os.path.exists(settings.MODEL_PATH)}", flush=True)
    print(f"File exists: {os.path.exists(file_path)}", flush=True)
    
    try:
        print(f"Calling ml_service.run_inference({file_path})...", flush=True)
        parsed = ml_service.run_inference(file_path) or {}
        print("ML inference complete!", flush=True)
        print(f"Parsed data type: {type(parsed)}", flush=True)
        print(f"Parsed data keys: {parsed.keys() if isinstance(parsed, dict) else 'N/A'}", flush=True)
        print(f"Parsed data: {parsed}", flush=True)
        logger.info("ML parsed output for receipt %s: %s", receipt_id, parsed)

        # Core parsed fields (using robust company extraction)
        print("Extracting fields...", flush=True)
        receipt.company_name = extract_company_name(parsed)
        print(f"Company: {receipt.company_name}", flush=True)
        
        receipt.receipt_date = parsed.get("receipt_date")
        print(f"Date: {receipt.receipt_date}", flush=True)
        
        receipt.receipt_address = parsed.get("receipt_address")
        print(f"Address: {receipt.receipt_address}", flush=True)
        
        receipt.total_amount = parsed.get("total_amount")
        print(f"Total: {receipt.total_amount}", flush=True)
        
        receipt.currency = parsed.get("currency", "KES")
        print(f"Currency: {receipt.currency}", flush=True)

        confidence = parsed.get("confidence") or 0.0
        receipt.overall_confidence = confidence
        receipt.confidence_company = confidence
        receipt.confidence_date = confidence
        receipt.confidence_address = confidence
        receipt.confidence_total = confidence
        print(f"Confidence: {confidence}", flush=True)

        # Store JSON-safe copy of full extraction
        if hasattr(receipt, "raw_extraction_json") and parsed is not None:
            print("Converting to JSON-safe format...", flush=True)
            receipt.raw_extraction_json = to_primitive(parsed)

        receipt.status = "completed"
        if hasattr(Receipt, "processing_completed_at"):
            receipt.processing_completed_at = datetime.utcnow()
        
        print("All fields extracted successfully", flush=True)

    except Exception as e:
        print("ERROR DURING ML PROCESSING:", flush=True)
        print(f"Error type: {type(e).__name__}", flush=True)
        print(f"Error message: {str(e)}", flush=True)
        print("Full traceback:", flush=True)
        import traceback
        traceback.print_exc()
        
        logger.exception("Error processing receipt %s: %s", receipt_id, e)
        receipt.status = "failed"
        receipt.error_message = f"{type(e).__name__}: {str(e)}"
        if hasattr(Receipt, "processing_completed_at"):
            receipt.processing_completed_at = datetime.utcnow()

    print("Saving receipt status to database...", flush=True)
    try:
        db.commit()
        db.refresh(receipt)
        print(f"Receipt saved with status: {receipt.status}", flush=True)
        if receipt.status == "failed":
            print(f"Error message saved: {receipt.error_message}", flush=True)
    except Exception as e:
        print(f"FAILED to save receipt: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise

    # Recalculate KYC score for this user after each upload
    if receipt.status == "completed":
        print("Calculating KYC score...", flush=True)
        try:
            scorer = KYCScorer(db)
            scorer.calculate_user_score(str(current_user.id))
            db.commit()
            print("KYC score calculated", flush=True)
        except Exception as e:
            print(f"Warning: KYC score calculation failed (non-critical): {e}", flush=True)
            logger.exception("Error recalculating KYC score after upload: %s", e)
    else:
        print("Skipping KYC score calculation (receipt failed)", flush=True)

    print(f"UPLOAD COMPLETE - Status: {receipt.status}", flush=True)
    print("=" * 80, flush=True)
    return receipt


@router.get("/{receipt_id}/file")
def get_receipt_file(
    receipt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    """
    Return the raw receipt file for viewing/downloading.
    """
    try:
        receipt_uuid = UUID(receipt_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid receipt id",
        )

    receipt = (
        db.query(Receipt)
        .filter(Receipt.id == receipt_uuid, Receipt.user_id == current_user.id)
        .first()
    )
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found",
        )

    if not receipt.file_path or not os.path.exists(receipt.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt file not found on server",
        )

    media_type = getattr(receipt, "file_type", None) or "application/octet-stream"
    return FileResponse(
        path=receipt.file_path,
        media_type=media_type,
        filename=receipt.file_name,
    )


@router.delete("/{receipt_id}")
def delete_receipt(
    receipt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a receipt (and its file) for the current user,
    then recalculate their KYC score.
    """
    try:
        receipt_uuid = UUID(receipt_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid receipt id",
        )

    receipt = (
        db.query(Receipt)
        .filter(Receipt.id == receipt_uuid, Receipt.user_id == current_user.id)
        .first()
    )
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found",
        )

    # Delete file from disk (ignore errors if already gone)
    if receipt.file_path and os.path.exists(receipt.file_path):
        try:
            os.remove(receipt.file_path)
        except OSError:
            pass

    db.delete(receipt)
    db.commit()

    # Recalculate KYC score after deletion
    try:
        scorer = KYCScorer(db)
        scorer.calculate_user_score(str(current_user.id))
        db.commit()
    except Exception as e:
        logger.exception("Error recalculating KYC score after delete: %s", e)

    return {"detail": "Receipt deleted"}


# Debug endpoints
@router.get("/debug/failed")
def get_failed_receipts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Debug endpoint to see failed receipts and their errors"""
    failed = (
        db.query(Receipt)
        .filter(
            Receipt.user_id == current_user.id,
            Receipt.status == "failed"
        )
        .order_by(Receipt.uploaded_at.desc())
        .limit(10)
        .all()
    )
    
    return [
        {
            "id": str(r.id),
            "file_name": r.file_name,
            "uploaded_at": r.uploaded_at.isoformat(),
            "error_message": r.error_message,
            "file_path": r.file_path,
        }
        for r in failed
    ]


@router.get("/debug/all-status")
def debug_all_receipts_status(db: Session = Depends(get_db)):
    """Show ALL receipts and their status (no auth for debugging)"""
    receipts = (
        db.query(Receipt)
        .order_by(Receipt.uploaded_at.desc())
        .limit(20)
        .all()
    )
    
    return {
        "total": len(receipts),
        "by_status": {
            "failed": len([r for r in receipts if r.status == "failed"]),
            "completed": len([r for r in receipts if r.status == "completed"]),
            "processing": len([r for r in receipts if r.status == "processing"]),
        },
        "receipts": [
            {
                "id": str(r.id),
                "file_name": r.file_name,
                "status": r.status,
                "error_message": r.error_message,
                "company_name": r.company_name,
                "total_amount": float(r.total_amount) if r.total_amount else None,
                "confidence": float(r.overall_confidence or 0.0),
                "uploaded_at": r.uploaded_at.isoformat(),
            }
            for r in receipts
        ]
    }


@router.get("/debug/model-status")
def debug_model_status():
    """Check ML model status"""
    return {
        "model_path": settings.MODEL_PATH,
        "model_path_exists": os.path.exists(settings.MODEL_PATH),
        "model_device": settings.MODEL_DEVICE,
        "ml_service_loaded": ml_service._loaded,
        "upload_dir": UPLOAD_DIR,
        "upload_dir_exists": os.path.exists(UPLOAD_DIR),
    }