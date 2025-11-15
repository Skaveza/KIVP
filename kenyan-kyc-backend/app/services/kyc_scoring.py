"""
KYC Scoring Service - Calculate Verification Scores
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import User, Receipt, VerificationScore
from app.core.config import settings
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class KYCScorer:
    """Service for calculating KYC verification scores"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_user_score(self, user_id: str) -> VerificationScore:
        """Calculate complete KYC score for a user"""
        
        # Get all completed receipts for user
        receipts = (
            self.db.query(Receipt)
            .filter(
                Receipt.user_id == user_id,
                Receipt.status == 'completed',
                Receipt.total_amount.isnot(None)
            )
            .all()
        )
        
        if not receipts:
            # No receipts, return zero scores
            return self._create_or_update_score(user_id, {
                'document_quality_score': Decimal('0.00'),
                'spending_pattern_score': Decimal('0.00'),
                'consistency_score': Decimal('0.00'),
                'diversity_score': Decimal('0.00'),
                'final_score': Decimal('0.00'),
                'is_verified': False,
                'total_receipts': 0,
                'total_spending': Decimal('0.00'),
                'unique_companies': 0,
                'unique_locations': 0,
                'date_range_days': 0,
                'average_transaction_amount': Decimal('0.00')
            })
        
        # Calculate each component
        doc_quality = self._calculate_document_quality_score(receipts)
        spending_pattern = self._calculate_spending_pattern_score(receipts)
        consistency = self._calculate_consistency_score(receipts)
        diversity = self._calculate_diversity_score(receipts)
        
        # Calculate final weighted score
        final_score = (
            doc_quality * Decimal(str(settings.WEIGHT_DOCUMENT_QUALITY)) +
            spending_pattern * Decimal(str(settings.WEIGHT_SPENDING_PATTERN)) +
            consistency * Decimal(str(settings.WEIGHT_CONSISTENCY)) +
            diversity * Decimal(str(settings.WEIGHT_DIVERSITY))
        )
        
        final_score = round(final_score, 2)
        is_verified = final_score >= Decimal(str(settings.VERIFICATION_THRESHOLD))
        
        # Calculate supporting metrics
        total_spending = sum(r.total_amount for r in receipts)
        unique_companies = len(set(r.company_name for r in receipts if r.company_name))
        unique_locations = len(set(r.receipt_address for r in receipts if r.receipt_address))
        
        dates = [r.receipt_date for r in receipts if r.receipt_date]
        date_range_days = 0
        if dates:
            date_range_days = (max(dates) - min(dates)).days
        
        avg_transaction = total_spending / len(receipts) if receipts else Decimal('0.00')
        
        score_data = {
            'document_quality_score': round(doc_quality, 2),
            'spending_pattern_score': round(spending_pattern, 2),
            'consistency_score': round(consistency, 2),
            'diversity_score': round(diversity, 2),
            'final_score': final_score,
            'is_verified': is_verified,
            'total_receipts': len(receipts),
            'total_spending': round(total_spending, 2),
            'unique_companies': unique_companies,
            'unique_locations': unique_locations,
            'date_range_days': date_range_days,
            'average_transaction_amount': round(avg_transaction, 2)
        }
        
        score = self._create_or_update_score(user_id, score_data)
        self._update_user_kyc_status(user_id, final_score, is_verified)
        
        logger.info(f"Calculated KYC score for user {user_id}: {final_score}")
        return score
    
    def _calculate_document_quality_score(self, receipts) -> Decimal:
        """Calculate based on ML extraction confidence (0-100)"""
        if not receipts:
            return Decimal('0.00')
        
        confidences = [r.overall_confidence for r in receipts if r.overall_confidence]
        if not confidences:
            return Decimal('0.00')
        
        avg_confidence = sum(confidences) / len(confidences)
        score = avg_confidence * Decimal('100')
        return min(score, Decimal('100.00'))
    
    def _calculate_spending_pattern_score(self, receipts) -> Decimal:
        """Calculate based on total amount and frequency (0-100)"""
        if not receipts:
            return Decimal('0.00')
        
        total_spending = sum(r.total_amount for r in receipts)
        receipt_count = len(receipts)
        
        # Spending score (0-60 points)
        if total_spending >= 100000:
            spending_score = Decimal('60.00')
        elif total_spending >= 50000:
            spending_score = Decimal('45.00')
        elif total_spending >= 25000:
            spending_score = Decimal('30.00')
        else:
            spending_score = (total_spending / Decimal('1000')) * Decimal('0.6')
        
        # Frequency score (0-40 points)
        if receipt_count >= 20:
            frequency_score = Decimal('40.00')
        elif receipt_count >= 10:
            frequency_score = Decimal('30.00')
        elif receipt_count >= 5:
            frequency_score = Decimal('20.00')
        else:
            frequency_score = Decimal(str(receipt_count)) * Decimal('4.00')
        
        total_score = spending_score + frequency_score
        return min(total_score, Decimal('100.00'))
    
    def _calculate_consistency_score(self, receipts) -> Decimal:
        """Calculate based on regular transactions over time (0-100)"""
        if not receipts:
            return Decimal('0.00')
        
        dates = [r.receipt_date for r in receipts if r.receipt_date]
        if not dates or len(dates) < 2:
            return Decimal('0.00')
        
        date_range_days = (max(dates) - min(dates)).days
        if date_range_days == 0:
            return Decimal('0.00')
        
        receipts_per_week = (len(receipts) / date_range_days) * 7
        
        if receipts_per_week >= 2:
            score = Decimal('100.00')
        elif receipts_per_week >= 1:
            score = Decimal('75.00')
        elif receipts_per_week >= 0.5:
            score = Decimal('50.00')
        else:
            score = Decimal(str(receipts_per_week)) * Decimal('50.00')
        
        if date_range_days >= 90:
            score = min(score + Decimal('10.00'), Decimal('100.00'))
        elif date_range_days >= 60:
            score = min(score + Decimal('5.00'), Decimal('100.00'))
        
        return min(score, Decimal('100.00'))
    
    def _calculate_diversity_score(self, receipts) -> Decimal:
        """Calculate based on different businesses and locations (0-100)"""
        if not receipts:
            return Decimal('0.00')
        
        unique_companies = len(set(r.company_name for r in receipts if r.company_name))
        unique_locations = len(set(r.receipt_address for r in receipts if r.receipt_address))
        
        # Company diversity (0-60 points)
        if unique_companies >= 5:
            company_score = Decimal('60.00')
        elif unique_companies >= 3:
            company_score = Decimal('45.00')
        elif unique_companies >= 2:
            company_score = Decimal('30.00')
        else:
            company_score = Decimal('15.00')
        
        # Location diversity (0-40 points)
        if unique_locations >= 3:
            location_score = Decimal('40.00')
        elif unique_locations >= 2:
            location_score = Decimal('25.00')
        else:
            location_score = Decimal('10.00')
        
        total_score = company_score + location_score
        return min(total_score, Decimal('100.00'))
    
    def _create_or_update_score(self, user_id: str, score_data: dict) -> VerificationScore:
        """Create or update verification score for user"""
        score = (
            self.db.query(VerificationScore)
            .filter(VerificationScore.user_id == user_id)
            .first()
        )
        
        if score:
            for key, value in score_data.items():
                setattr(score, key, value)
            score.calculated_at = datetime.utcnow()
        else:
            score = VerificationScore(user_id=user_id, **score_data)
            self.db.add(score)
        
        self.db.commit()
        self.db.refresh(score)
        return score
    
    def _update_user_kyc_status(self, user_id: str, score: Decimal, is_verified: bool):
        """Update user's KYC status based on score"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return
        
        user.kyc_score = score
        
        if is_verified:
            user.kyc_status = 'verified'
            if not user.verification_date:
                user.verification_date = datetime.utcnow()
        elif score >= 60:
            user.kyc_status = 'under_review'
        else:
            user.kyc_status = 'pending'
        
        self.db.commit()
