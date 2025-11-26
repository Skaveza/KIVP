"""
Verification/KYC Score API Routes
"""

from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.models import User, VerificationScore, Receipt
from app.schemas.schemas import VerificationScoreResponse, MessageResponse
from app.api.dependencies import get_current_user
from app.services.kyc_scoring import KYCScorer

router = APIRouter(prefix="/verification", tags=["Verification"])


@router.get("/score", response_model=VerificationScoreResponse)
def get_verification_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's KYC verification score."""
    score = (
        db.query(VerificationScore)
        .filter(VerificationScore.user_id == current_user.id)
        .first()
    )

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verification score found. Upload receipts to get scored.",
        )

    return score


@router.post("/calculate", response_model=VerificationScoreResponse)
def calculate_verification_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually trigger KYC score calculation."""
    scorer = KYCScorer(db)
    score = scorer.calculate_user_score(str(current_user.id))
    return score


@router.get("/history")
def get_score_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get historical KYC score changes (if you decide to keep this table)."""
    history = db.execute(
        """
        SELECT 
            final_score,
            total_receipts_at_time,
            recorded_at
        FROM verification_history
        WHERE user_id = :user_id
        ORDER BY recorded_at ASC
        """,
        {"user_id": str(current_user.id)},
    ).fetchall()

    return [
        {
            "score": float(record[0]),
            "receipts": record[1],
            "date": record[2].isoformat(),
        }
        for record in history
    ]


@router.get("/breakdown")
def get_score_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed breakdown of KYC score calculation + which receipts were used/ignored.
    """
    score = (
        db.query(VerificationScore)
        .filter(VerificationScore.user_id == current_user.id)
        .first()
    )

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verification score found",
        )

    # Use the same weights as in KYCScorer
    w_doc = Decimal(str(settings.WEIGHT_DOCUMENT_QUALITY))
    w_spend = Decimal(str(settings.WEIGHT_SPENDING_PATTERN))
    w_cons = Decimal(str(settings.WEIGHT_CONSISTENCY))
    w_div = Decimal(str(settings.WEIGHT_DIVERSITY))

    # Contributions
    doc_contribution = Decimal(score.document_quality_score) * w_doc
    spending_contribution = Decimal(score.spending_pattern_score) * w_spend
    consistency_contribution = Decimal(score.consistency_score) * w_cons
    diversity_contribution = Decimal(score.diversity_score) * w_div

    # Partition receipts using the same logic as scoring
    scorer = KYCScorer(db)
    trusted, dropped = scorer.partition_receipts_for_user(str(current_user.id))

    receipts_used = [
        {
            "id": str(r.id),
            "file_name": r.file_name,
            "company_name": r.company_name,
            "receipt_date": r.receipt_date.isoformat() if r.receipt_date else None,
            "total_amount": float(r.total_amount)
            if r.total_amount is not None
            else None,
            "currency": r.currency,
            "overall_confidence": float(r.overall_confidence or 0.0),
        }
        for r in trusted
    ]

    receipts_dropped = [
        {
            "id": str(r.id),
            "file_name": r.file_name,
            "total_amount": float(r.total_amount)
            if r.total_amount is not None
            else None,
            "currency": r.currency,
            "overall_confidence": float(r.overall_confidence or 0.0),
            "reason_if_dropped": reason,
        }
        for (r, reason) in dropped
    ]

    return {
        "final_score": float(score.final_score),
        "is_verified": score.is_verified,
        "verification_threshold": float(score.verification_threshold),
        "components": [
            {
                "name": "Document Quality",
                "score": float(score.document_quality_score),
                "weight": float(w_doc),
                "contribution": float(round(doc_contribution, 2)),
                "description": "Based on ML extraction confidence from receipts",
                "tip": "Upload clear, high-quality receipt images",
            },
            {
                "name": "Spending Pattern",
                "score": float(score.spending_pattern_score),
                "weight": float(w_spend),
                "contribution": float(round(spending_contribution, 2)),
                "description": "Based on total spending and transaction frequency",
                "tip": "Upload more receipts from regular shopping",
            },
            {
                "name": "Consistency",
                "score": float(score.consistency_score),
                "weight": float(w_cons),
                "contribution": float(round(consistency_contribution, 2)),
                "description": "Based on regular transactions over time",
                "tip": "Upload receipts regularly over several weeks",
            },
            {
                "name": "Diversity",
                "score": float(score.diversity_score),
                "weight": float(w_div),
                "contribution": float(round(diversity_contribution, 2)),
                "description": "Based on variety of businesses and locations",
                "tip": f"Shop at different stores (currently {score.unique_companies} unique)",
            },
        ],
        "metrics": {
            "total_receipts": score.total_receipts,
            "total_spending": float(score.total_spending),
            "unique_companies": score.unique_companies,
            "unique_locations": score.unique_locations,
            "date_range_days": score.date_range_days,
            "average_transaction_amount": float(score.average_transaction_amount),
        },
        "receipts_used": receipts_used,
        "receipts_dropped": receipts_dropped,
    }


@router.get("/requirements")
def get_verification_requirements(current_user: User = Depends(get_current_user)):
    """Get requirements for KYC verification."""
    return {
        "verification_threshold": 75,
        "current_score": float(current_user.kyc_score or 0.0),
        "status": current_user.kyc_status,
        "is_verified": current_user.kyc_status == "verified",
        "requirements": {
            "minimum_score": 75,
            "recommended_receipts": "10+ receipts for accurate scoring",
            "timeframe": "Receipts should span at least 2-4 weeks",
            "diversity": "Upload receipts from 3+ different businesses",
            "quality": "Ensure receipt images are clear and readable",
        },
        "tips": [
            "Upload clear, well-lit photos of receipts",
            "Include receipts from different stores",
            "Upload receipts regularly over several weeks",
            "Ensure date, amount, and store name are visible",
            "Minimum 5 receipts recommended, 10+ for best results",
        ],
    }


# Add this to your verification.py
@router.get("/debug/breakdown-no-auth")
def get_score_breakdown_debug(
    user_id: str,  # Pass user_id as query param
    db: Session = Depends(get_db),
):
    """DEBUG ONLY - No auth required"""
    score = (
        db.query(VerificationScore)
        .filter(VerificationScore.user_id == user_id)
        .first()
    )

    if not score:
        return {"error": "No score found for this user"}

    scorer = KYCScorer(db)
    trusted, dropped = scorer.partition_receipts_for_user(user_id)

    return {
        "final_score": float(score.final_score),
        "receipts_used_count": len(trusted),
        "receipts_dropped": [
            {
                "id": str(r.id),
                "file_name": r.file_name,
                "reason": reason,
                "status": r.status,
                "error_message": r.error_message,
                "confidence": float(r.overall_confidence or 0.0),
            }
            for (r, reason) in dropped
        ]
    }

@router.get("/debug/all-scores")
def debug_all_scores(db: Session = Depends(get_db)):
    """Show all users and their verification scores"""
    from app.models.models import User, VerificationScore, Receipt
    
    users = db.query(User).all()
    
    result = []
    for user in users:
        score = db.query(VerificationScore).filter(
            VerificationScore.user_id == user.id
        ).first()
        
        receipts = db.query(Receipt).filter(
            Receipt.user_id == user.id
        ).all()
        
        result.append({
            "user_id": str(user.id),
            "email": user.email,
            "has_score": score is not None,
            "score_value": float(score.final_score) if score else None,
            "total_receipts": len(receipts),
            "failed_receipts": len([r for r in receipts if r.status == "failed"]),
            "completed_receipts": len([r for r in receipts if r.status == "completed"]),
        })
    
    return {
        "total_users": len(users),
        "users": result
    }