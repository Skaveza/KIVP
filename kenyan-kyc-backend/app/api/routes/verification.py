"""
Verification/KYC Score API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User, VerificationScore
from app.schemas.schemas import VerificationScoreResponse, MessageResponse
from app.api.dependencies import get_current_user
from app.services.kyc_scoring import KYCScorer

router = APIRouter(prefix="/verification", tags=["Verification"])


@router.get("/score", response_model=VerificationScoreResponse)
def get_verification_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's KYC verification score"""
    
    score = (
        db.query(VerificationScore)
        .filter(VerificationScore.user_id == current_user.id)
        .first()
    )
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verification score found. Upload receipts to get scored."
        )
    
    return score


@router.post("/calculate", response_model=VerificationScoreResponse)
def calculate_verification_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger KYC score calculation"""
    
    scorer = KYCScorer(db)
    score = scorer.calculate_user_score(str(current_user.id))
    
    return score


@router.get("/history")
def get_score_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical KYC score changes"""
    
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
        {"user_id": str(current_user.id)}
    ).fetchall()
    
    return [
        {
            "score": float(record[0]),
            "receipts": record[1],
            "date": record[2].isoformat()
        }
        for record in history
    ]


@router.get("/breakdown")
def get_score_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed breakdown of KYC score calculation"""
    
    score = (
        db.query(VerificationScore)
        .filter(VerificationScore.user_id == current_user.id)
        .first()
    )
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verification score found"
        )
    
    # Calculate contribution of each component
    doc_contribution = float(score.document_quality_score) * float(score.weight_document_quality)
    spending_contribution = float(score.spending_pattern_score) * float(score.weight_spending_pattern)
    consistency_contribution = float(score.consistency_score) * float(score.weight_consistency)
    diversity_contribution = float(score.diversity_score) * float(score.weight_diversity)
    
    return {
        "final_score": float(score.final_score),
        "is_verified": score.is_verified,
        "verification_threshold": float(score.verification_threshold),
        "components": [
            {
                "name": "Document Quality",
                "score": float(score.document_quality_score),
                "weight": float(score.weight_document_quality),
                "contribution": round(doc_contribution, 2),
                "description": "Based on ML extraction confidence from receipts",
                "tip": "Upload clear, high-quality receipt images"
            },
            {
                "name": "Spending Pattern",
                "score": float(score.spending_pattern_score),
                "weight": float(score.weight_spending_pattern),
                "contribution": round(spending_contribution, 2),
                "description": "Based on total spending and transaction frequency",
                "tip": "Upload more receipts from regular shopping"
            },
            {
                "name": "Consistency",
                "score": float(score.consistency_score),
                "weight": float(score.weight_consistency),
                "contribution": round(consistency_contribution, 2),
                "description": "Based on regular transactions over time",
                "tip": "Upload receipts regularly over several weeks"
            },
            {
                "name": "Diversity",
                "score": float(score.diversity_score),
                "weight": float(score.weight_diversity),
                "contribution": round(diversity_contribution, 2),
                "description": "Based on variety of businesses and locations",
                "tip": f"Shop at different stores (currently {score.unique_companies} unique)"
            }
        ],
        "metrics": {
            "total_receipts": score.total_receipts,
            "total_spending": float(score.total_spending),
            "unique_companies": score.unique_companies,
            "unique_locations": score.unique_locations,
            "date_range_days": score.date_range_days
        }
    }


@router.get("/requirements")
def get_verification_requirements(current_user: User = Depends(get_current_user)):
    """Get requirements for KYC verification"""
    
    return {
        "verification_threshold": 75,
        "current_score": float(current_user.kyc_score),
        "status": current_user.kyc_status,
        "is_verified": current_user.kyc_status == 'verified',
        "requirements": {
            "minimum_score": 75,
            "recommended_receipts": "10+ receipts for accurate scoring",
            "timeframe": "Receipts should span at least 2-4 weeks",
            "diversity": "Upload receipts from 3+ different businesses",
            "quality": "Ensure receipt images are clear and readable"
        },
        "tips": [
            "Upload clear, well-lit photos of receipts",
            "Include receipts from different stores",
            "Upload receipts regularly over several weeks",
            "Ensure date, amount, and store name are visible",
            "Minimum 5 receipts recommended, 10+ for best results"
        ]
    }
