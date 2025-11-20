from decimal import Decimal
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from app.models.models import User, Receipt, VerificationScore
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global KYC thresholds 
MIN_RECEIPT_CONFIDENCE = Decimal(
    str(getattr(settings, "MIN_RECEIPT_CONFIDENCE", 0.95))
)
_max_single_raw = getattr(settings, "MAX_SINGLE_RECEIPT_KES", 200_000.0)
MAX_SINGLE_RECEIPT_KES = (
    Decimal(str(_max_single_raw)) if _max_single_raw is not None else None
)


class KYCScorer:
    """Service for calculating KYC verification scores with confidence + outlier filtering."""

    def __init__(self, db: Session):
        self.db = db


    # Partition receipts: trusted vs dropped
    def partition_receipts_for_user(self, user_id: str):
        """Return (trusted_receipts, dropped_receipts_with_reasons)."""

        all_receipts = (
            self.db.query(Receipt)
            .filter(
                Receipt.user_id == user_id,
                Receipt.status == "completed",
                Receipt.total_amount.isnot(None),
            )
            .order_by(Receipt.uploaded_at.asc())
            .all()
        )

        trusted = []
        dropped = []

        for r in all_receipts:
            reasons = []

            # 0) Missing or placeholder company name
            if not r.company_name or str(r.company_name).strip().lower() in (
                "unknown",
                "n/a",
            ):
                reasons.append("missing_company_name")

            # 1) Confidence filter
            conf = Decimal(str(r.overall_confidence or 0.0))
            if conf < MIN_RECEIPT_CONFIDENCE:
                reasons.append(
                    f"low_confidence ({float(conf):.3f} < {float(MIN_RECEIPT_CONFIDENCE):.3f})"
                )

            # 2) Outlier filter on total amount
            if (
                MAX_SINGLE_RECEIPT_KES is not None
                and r.total_amount is not None
                and Decimal(str(r.total_amount)) > MAX_SINGLE_RECEIPT_KES
            ):
                reasons.append(
                    f"outlier_amount ({r.total_amount} > {float(MAX_SINGLE_RECEIPT_KES):.0f})"
                )

            if reasons:
                dropped.append((r, "; ".join(reasons)))
            else:
                trusted.append(r)

        logger.info(
            f"KYCScorer.partition_receipts_for_user user={user_id}: "
            f"trusted={len(trusted)}, dropped={len(dropped)}, "
            f"min_conf={float(MIN_RECEIPT_CONFIDENCE)}, "
            f"max_single={float(MAX_SINGLE_RECEIPT_KES) if MAX_SINGLE_RECEIPT_KES else None}"
        )
        for r, reason in dropped:
            logger.info(
                "KYCScorer: dropping receipt id=%s file=%s reason=%s",
                r.id,
                r.file_name,
                reason,
            )

        return trusted, dropped

    # -------------------------------------------------
    # Main scoring entry point
    # -------------------------------------------------
    def calculate_user_score(self, user_id: str) -> VerificationScore:
        # Use filtered receipts
        receipts, dropped = self.partition_receipts_for_user(user_id)

        # If nothing trusted → 0 score
        if not receipts:
            zero_data = {
                "document_quality_score": Decimal("0.00"),
                "spending_pattern_score": Decimal("0.00"),
                "consistency_score": Decimal("0.00"),
                "diversity_score": Decimal("0.00"),
                "final_score": Decimal("0.00"),
                "is_verified": False,
                "total_receipts": 0,
                "total_spending": Decimal("0.00"),
                "unique_companies": 0,
                "unique_locations": 0,
                "date_range_days": 0,
                "average_transaction_amount": Decimal("0.00"),
            }
            score = self._create_or_update_score(user_id, zero_data)
            self._update_user_kyc_status(user_id, score.final_score, score.is_verified)
            logger.info(
                "KYCScorer.calculate_user_score user=%s: no trusted receipts → score=0",
                user_id,
            )
            return score

        # Component scores
        doc_quality = self._calculate_document_quality_score(receipts)
        spending_pattern = self._calculate_spending_pattern_score(receipts)
        consistency = self._calculate_consistency_score(receipts)
        diversity = self._calculate_diversity_score(receipts)

        # Weighted final score
        final_score = (
            doc_quality * Decimal(str(settings.WEIGHT_DOCUMENT_QUALITY))
            + spending_pattern * Decimal(str(settings.WEIGHT_SPENDING_PATTERN))
            + consistency * Decimal(str(settings.WEIGHT_CONSISTENCY))
            + diversity * Decimal(str(settings.WEIGHT_DIVERSITY))
        ).quantize(Decimal("0.01"))

        is_verified = final_score >= Decimal(str(settings.VERIFICATION_THRESHOLD))

        # Aggregate metrics (only on trusted receipts)
        total_spending = sum(
            (
                Decimal(str(r.total_amount))
                for r in receipts
                if r.total_amount is not None
            ),
            start=Decimal("0.00"),
        )
        unique_companies = len({r.company_name for r in receipts if r.company_name})
        unique_locations = len({r.receipt_address for r in receipts if r.receipt_address})
        dates = [r.receipt_date for r in receipts if r.receipt_date]
        date_range_days = (max(dates) - min(dates)).days if dates else 0
        avg_transaction = (
            total_spending / len(receipts) if receipts else Decimal("0.00")
        )

        score_data = {
            "document_quality_score": doc_quality.quantize(Decimal("0.01")),
            "spending_pattern_score": spending_pattern.quantize(Decimal("0.01")),
            "consistency_score": consistency.quantize(Decimal("0.01")),
            "diversity_score": diversity.quantize(Decimal("0.01")),
            "final_score": final_score,
            "is_verified": is_verified,
            "total_receipts": len(receipts),
            "total_spending": total_spending.quantize(Decimal("0.01")),
            "unique_companies": unique_companies,
            "unique_locations": unique_locations,
            "date_range_days": date_range_days,
            "average_transaction_amount": avg_transaction.quantize(Decimal("0.01")),
        }

        score = self._create_or_update_score(user_id, score_data)
        self._update_user_kyc_status(user_id, final_score, is_verified)

        logger.info(
            "KYCScorer.calculate_user_score user=%s: final_score=%s, verified=%s, "
            "trusted_receipts=%d, dropped_receipts=%d",
            user_id,
            final_score,
            is_verified,
            len(receipts),
            len(dropped),
        )
        return score

    # -------------------------------------------------
    # Component calculations
    # -------------------------------------------------
    def _calculate_document_quality_score(self, receipts) -> Decimal:
        confidences = [
            Decimal(str(r.overall_confidence))
            for r in receipts
            if r.overall_confidence is not None
        ]
        if not confidences:
            return Decimal("0.00")
        avg_confidence = sum(confidences) / len(confidences)
        return min(avg_confidence * Decimal("100"), Decimal("100.00"))

    def _calculate_spending_pattern_score(self, receipts) -> Decimal:
        if not receipts:
            return Decimal("0.00")

        amounts_with_conf = [
            Decimal(str(r.total_amount))
            for r in receipts
            if r.total_amount is not None and r.confidence_total is not None
        ]

        if not amounts_with_conf:
            total_conf = Decimal("0.50")
        else:
            weighted_sum = sum(
                Decimal(str(r.confidence_total)) * Decimal(str(r.total_amount))
                for r in receipts
                if r.total_amount is not None and r.confidence_total is not None
            )
            denom = sum(amounts_with_conf)
            total_conf = weighted_sum / denom if denom > 0 else Decimal("0.50")

        total_spending = sum(
            (Decimal(str(r.total_amount)) for r in receipts if r.total_amount is not None),
            start=Decimal("0.00"),
        )
        receipt_count = len(receipts)

        # Spending score (0–60)
        if total_spending >= Decimal("100000"):
            spending_score = Decimal("60.00")
        elif total_spending >= Decimal("50000"):
            spending_score = Decimal("45.00")
        elif total_spending >= Decimal("25000"):
            spending_score = Decimal("30.00")
        else:
            spending_score = (total_spending / Decimal("1000")) * Decimal("0.60")

        # Frequency score (0–40)
        if receipt_count >= 20:
            frequency_score = Decimal("40.00")
        elif receipt_count >= 10:
            frequency_score = Decimal("30.00")
        elif receipt_count >= 5:
            frequency_score = Decimal("20.00")
        else:
            frequency_score = Decimal(str(receipt_count)) * Decimal("4.00")

        total_score = (spending_score + frequency_score) * total_conf
        return min(total_score, Decimal("100.00"))

    def _calculate_consistency_score(self, receipts) -> Decimal:
        if not receipts:
            return Decimal("0.00")

        dates = [r.receipt_date for r in receipts if r.receipt_date]
        if len(dates) < 2:
            return Decimal("0.00")

        date_range_days = (max(dates) - min(dates)).days
        if date_range_days == 0:
            return Decimal("0.00")

        receipts_per_week = (len(receipts) / date_range_days) * 7

        if receipts_per_week >= 2:
            score = Decimal("100.00")
        elif receipts_per_week >= 1:
            score = Decimal("75.00")
        elif receipts_per_week >= 0.5:
            score = Decimal("50.00")
        else:
            score = Decimal(str(receipts_per_week * 50))

        if date_range_days >= 90:
            score = min(score + Decimal("10.00"), Decimal("100.00"))
        elif date_range_days >= 60:
            score = min(score + Decimal("5.00"), Decimal("100.00"))

        date_confidences = [
            Decimal(str(r.confidence_date))
            for r in receipts
            if r.confidence_date is not None
        ]
        avg_date_conf = (
            sum(date_confidences) / len(date_confidences)
            if date_confidences
            else Decimal("0.50")
        )
        score *= max(avg_date_conf, Decimal("0.50"))
        return min(score, Decimal("100.00"))

    def _calculate_diversity_score(self, receipts) -> Decimal:
        if not receipts:
            return Decimal("0.00")

        unique_companies = {r.company_name for r in receipts if r.company_name}
        unique_locations = {r.receipt_address for r in receipts if r.receipt_address}

        if len(unique_companies) >= 5:
            company_score = Decimal("60.00")
        elif len(unique_companies) >= 3:
            company_score = Decimal("45.00")
        elif len(unique_companies) >= 2:
            company_score = Decimal("30.00")
        else:
            company_score = Decimal("15.00")

        if len(unique_locations) >= 3:
            location_score = Decimal("40.00")
        elif len(unique_locations) >= 2:
            location_score = Decimal("25.00")
        else:
            location_score = Decimal("10.00")

        company_confs = [
            Decimal(str(r.confidence_company))
            for r in receipts
            if r.confidence_company is not None
        ]
        address_confs = [
            Decimal(str(r.confidence_address))
            for r in receipts
            if r.confidence_address is not None
        ]

        if company_confs:
            avg_company_conf = sum(company_confs) / len(company_confs)
        else:
            avg_company_conf = Decimal("0.50")

        if address_confs:
            avg_address_conf = sum(address_confs) / len(address_confs)
        else:
            avg_address_conf = Decimal("0.50")

        avg_conf = (avg_company_conf + avg_address_conf) / 2
        total_score = (company_score + location_score) * avg_conf
        return min(total_score, Decimal("100.00"))

    # -------------------------------------------------
    # Persistence + user status
    # -------------------------------------------------
    def _create_or_update_score(self, user_id: str, score_data: dict) -> VerificationScore:
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
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        user.kyc_score = score

        if is_verified:
            user.kyc_status = "verified"
            if not user.verification_date:
                user.verification_date = datetime.utcnow()
        elif score >= Decimal("60.00"):
            user.kyc_status = "under_review"
        else:
            user.kyc_status = "pending"

        self.db.commit()
