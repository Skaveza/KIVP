"""
User Management API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.models import User, Receipt, VerificationScore
from app.schemas.schemas import UserResponse, UserUpdate, UserDashboard, ReceiptResponse
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user


@router.patch("/profile", response_model=UserResponse)
def update_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    
    if updates.full_name is not None:
        current_user.full_name = updates.full_name
    
    if updates.phone_number is not None:
        current_user.phone_number = updates.phone_number
    
    if updates.national_id is not None:
        current_user.national_id = updates.national_id
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/dashboard", response_model=UserDashboard)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's complete dashboard data"""
    
    # Get verification score
    verification_score = (
        db.query(VerificationScore)
        .filter(VerificationScore.user_id == current_user.id)
        .first()
    )
    
    # Get recent receipts (last 10)
    recent_receipts = (
        db.query(Receipt)
        .filter(Receipt.user_id == current_user.id)
        .order_by(Receipt.uploaded_at.desc())
        .limit(10)
        .all()
    )
    
    # Get receipt counts
    total_receipts = (
        db.query(func.count(Receipt.id))
        .filter(Receipt.user_id == current_user.id)
        .scalar()
    )
    
    processed_receipts = (
        db.query(func.count(Receipt.id))
        .filter(
            Receipt.user_id == current_user.id,
            Receipt.status == 'completed'
        )
        .scalar()
    )
    
    pending_receipts = (
        db.query(func.count(Receipt.id))
        .filter(
            Receipt.user_id == current_user.id,
            Receipt.status.in_(['pending', 'processing'])
        )
        .scalar()
    )
    
    return {
        "user": current_user,
        "verification_score": verification_score,
        "recent_receipts": recent_receipts,
        "total_receipts": total_receipts or 0,
        "processed_receipts": processed_receipts or 0,
        "pending_receipts": pending_receipts or 0
    }


@router.get("/stats")
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's statistical data for charts/graphs"""
    
    # Receipt counts by status
    receipt_counts = (
        db.query(Receipt.status, func.count(Receipt.id))
        .filter(Receipt.user_id == current_user.id)
        .group_by(Receipt.status)
        .all()
    )
    
    # Spending by company
    spending_by_company = (
        db.query(
            Receipt.company_name,
            func.count(Receipt.id).label('receipt_count'),
            func.sum(Receipt.total_amount).label('total_spent')
        )
        .filter(
            Receipt.user_id == current_user.id,
            Receipt.status == 'completed',
            Receipt.company_name.isnot(None)
        )
        .group_by(Receipt.company_name)
        .order_by(func.sum(Receipt.total_amount).desc())
        .limit(10)
        .all()
    )
    
    return {
        "receipt_counts": [{"status": status, "count": count} for status, count in receipt_counts],
        "spending_by_company": [
            {
                "company": company,
                "receipt_count": count,
                "total_spent": float(total)
            }
            for company, count, total in spending_by_company
        ]
    }
