"""
Admin API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.models.models import User, Receipt, VerificationScore
from app.schemas.schemas import UserResponse, AdminStatistics
from app.api.dependencies import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    kyc_status: str = None,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (Admin only)"""
    
    query = db.query(User).filter(User.account_type == 'investor')
    
    if kyc_status:
        query = query.filter(User.kyc_status == kyc_status)
    
    users = (
        query
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return users


@router.get("/statistics", response_model=AdminStatistics)
def get_platform_statistics(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get platform statistics (Admin only)"""
    
    total_users = (
        db.query(func.count(User.id))
        .filter(User.account_type == 'investor')
        .scalar()
    )
    
    verified_users = (
        db.query(func.count(User.id))
        .filter(User.account_type == 'investor', User.kyc_status == 'verified')
        .scalar()
    )
    
    pending_users = (
        db.query(func.count(User.id))
        .filter(User.account_type == 'investor', User.kyc_status == 'pending')
        .scalar()
    )
    
    under_review_users = (
        db.query(func.count(User.id))
        .filter(User.account_type == 'investor', User.kyc_status == 'under_review')
        .scalar()
    )
    
    total_receipts = db.query(func.count(Receipt.id)).scalar()
    
    processed_receipts = (
        db.query(func.count(Receipt.id))
        .filter(Receipt.status == 'completed')
        .scalar()
    )
    
    failed_receipts = (
        db.query(func.count(Receipt.id))
        .filter(Receipt.status == 'failed')
        .scalar()
    )
    
    total_spending = (
        db.query(func.sum(Receipt.total_amount))
        .filter(Receipt.status == 'completed')
        .scalar()
    ) or 0
    
    avg_score = (
        db.query(func.avg(VerificationScore.final_score))
        .scalar()
    ) or 0
    
    return {
        "total_users": total_users or 0,
        "verified_users": verified_users or 0,
        "pending_users": pending_users or 0,
        "under_review_users": under_review_users or 0,
        "total_receipts": total_receipts or 0,
        "processed_receipts": processed_receipts or 0,
        "failed_receipts": failed_receipts or 0,
        "total_platform_spending": total_spending,
        "average_kyc_score": round(avg_score, 2)
    }


@router.patch("/users/{user_id}/verify", response_model=UserResponse)
def manually_verify_user(
    user_id: str,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Manually verify user (Admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    from datetime import datetime
    
    user.kyc_status = 'verified'
    user.verification_date = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return user