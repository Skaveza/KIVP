"""
Receipt Management API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.models.models import User, Receipt
from app.schemas.schemas import ReceiptResponse, MessageResponse
from app.api.dependencies import get_current_user
from app.utils.file_utils import save_upload_file, delete_file
from app.services.kyc_scoring import KYCScorer

router = APIRouter(prefix="/receipts", tags=["Receipts"])


@router.post("/upload", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
async def upload_receipt(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a receipt image for processing"""
    
    # Save uploaded file
    original_filename, file_path, file_size = await save_upload_file(file, str(current_user.id))
    
    # Create receipt record
    new_receipt = Receipt(
        user_id=current_user.id,
        file_name=original_filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file.content_type,
        status='pending'
    )
    
    db.add(new_receipt)
    db.commit()
    db.refresh(new_receipt)
    
    return new_receipt


@router.get("/", response_model=List[ReceiptResponse])
def get_receipts(
    skip: int = 0,
    limit: int = 50,
    status_filter: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all receipts for current user"""
    
    query = db.query(Receipt).filter(Receipt.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Receipt.status == status_filter)
    
    receipts = (
        query
        .order_by(Receipt.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return receipts


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(
    receipt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific receipt"""
    
    receipt = (
        db.query(Receipt)
        .filter(
            Receipt.id == receipt_id,
            Receipt.user_id == current_user.id
        )
        .first()
    )
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    return receipt


@router.delete("/{receipt_id}", response_model=MessageResponse)
def delete_receipt(
    receipt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a receipt"""
    
    receipt = (
        db.query(Receipt)
        .filter(
            Receipt.id == receipt_id,
            Receipt.user_id == current_user.id
        )
        .first()
    )
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    # Delete file from storage
    delete_file(receipt.file_path)
    
    # Delete from database
    db.delete(receipt)
    db.commit()
    
    # Recalculate KYC score
    scorer = KYCScorer(db)
    scorer.calculate_user_score(str(current_user.id))
    
    return {"message": "Receipt deleted successfully", "success": True}


@router.post("/{receipt_id}/process", response_model=ReceiptResponse)
def process_receipt(
    receipt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger processing for a receipt (DEMO MODE).
    Uses mock data - replace with your ML model.
    """
    
    receipt = (
        db.query(Receipt)
        .filter(
            Receipt.id == receipt_id,
            Receipt.user_id == current_user.id
        )
        .first()
    )
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    if receipt.status == 'completed':
        return receipt
    
    # Update status to processing
    receipt.status = 'processing'
    receipt.processing_started_at = datetime.utcnow()
    db.commit()
    
    # TODO: Call your ML model here
    # For demo, use mock data:
    from decimal import Decimal
    from datetime import date
    
    receipt.status = 'completed'
    receipt.company_name = 'Naivas Supermarket'
    receipt.receipt_date = date.today()
    receipt.receipt_address = 'Nairobi, Kenya'
    receipt.total_amount = Decimal('2500.00')
    receipt.currency = 'KES'
    receipt.confidence_company = Decimal('0.95')
    receipt.confidence_date = Decimal('0.92')
    receipt.confidence_address = Decimal('0.88')
    receipt.confidence_total = Decimal('0.97')
    receipt.overall_confidence = Decimal('0.93')
    receipt.raw_extraction_json = {
        "company": "Naivas Supermarket",
        "date": str(date.today()),
        "address": "Nairobi, Kenya",
        "total": "2500.00"
    }
    receipt.processing_completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(receipt)
    
    # Recalculate KYC score
    scorer = KYCScorer(db)
    scorer.calculate_user_score(str(current_user.id))
    
    return receipt


@router.get("/stats/summary")
def get_receipt_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary statistics about user's receipts"""
    from sqlalchemy import func
    
    stats = db.query(
        func.count(Receipt.id).label('total'),
        func.count(Receipt.id).filter(Receipt.status == 'completed').label('completed'),
        func.count(Receipt.id).filter(Receipt.status == 'pending').label('pending'),
        func.count(Receipt.id).filter(Receipt.status == 'failed').label('failed'),
        func.sum(Receipt.total_amount).filter(Receipt.status == 'completed').label('total_spending')
    ).filter(Receipt.user_id == current_user.id).first()
    
    return {
        "total_receipts": stats.total or 0,
        "completed_receipts": stats.completed or 0,
        "pending_receipts": stats.pending or 0,
        "failed_receipts": stats.failed or 0,
        "total_spending": float(stats.total_spending or 0)
    }
