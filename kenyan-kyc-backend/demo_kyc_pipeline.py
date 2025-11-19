# demo_kyc_pipeline.py


from pathlib import Path
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.models import User, Receipt
from app.services.ml_service import ml_service
from app.services.kyc_scoring import KYCScorer


# Ground truth totals for your 3 demo receipts
GROUND_TRUTH_TOTALS = {
    "test2.jpg": Decimal("70.00"),    # NATVAS (model currently hallucinates 2,132,779)
    "test5.jpeg": Decimal("410.00"),  # Java House
    "test6.jpg": Decimal("6450.00"),  # Clean supermarket receipt
}


def main():
    db: Session = SessionLocal()

    try:
        # 1) Pick an existing user
        user = db.query(User).first()
        if not user:
            print(" No users found in DB.")
            print("   → Register a user via your existing API/frontend, then re-run this script.")
            return

        print(f" Using user: {user.email} (id={user.id})")

        # 2) Load test receipt images
        receipts_dir = Path("tests/demo_receipts")
        if not receipts_dir.exists():
            print(f" Folder {receipts_dir} not found. Create it and add your demo receipts.")
            return

        image_paths = sorted(
            p for p in receipts_dir.iterdir()
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        )

        if not image_paths:
            print(" No images found in tests/demo_receipts.")
            return

        print(f" Found {len(image_paths)} test receipts.")

        # Thresholds (mirror backend scoring)
        min_conf = Decimal(str(settings.MIN_RECEIPT_CONFIDENCE))
        max_amt = Decimal(str(getattr(settings, "MAX_SINGLE_RECEIPT_KES", 100000)))

        # 3) Run inference + save receipts
        for img_path in image_paths:
            print(f"\n🔍 Processing {img_path.name} ...")
            parsed = ml_service.run_inference(str(img_path))

            company = parsed.get("company_name")
            r_date = parsed.get("receipt_date")
            total = parsed.get("total_amount")
            currency = parsed.get("currency", "KES")
            confidence = parsed.get("confidence") or 0.0

            # Coerce for numeric logic
            total_dec = (
                Decimal(str(total))
                if total is not None
                else None
            )
            conf_dec = Decimal(str(confidence))

            print(f"  Company: {company}")
            print(f"  Date:    {r_date}")
            print(f"  Total:   {total} {currency}")
            print(f"  Conf:    {round(confidence, 4)}")

            # Ground truth comparison (for thesis/demo, not production)
            gt = GROUND_TRUTH_TOTALS.get(img_path.name)
            if gt is not None and total_dec is not None:
                if gt != 0:
                    error_pct = abs((total_dec - gt) / gt) * Decimal("100")
                    print(f"  Ground truth total: {gt}")
                    print(f"  Error vs ground truth: {float(error_pct):.1f}%")
                else:
                    print("  Ground truth total is 0 → skipping % error calculation.")
            elif gt is not None:
                print(f"  Ground truth total: {gt} (model returned no total)")
            else:
                print("  Ground truth total: (not defined for this demo image)")

            # Show whether this receipt will be trusted by the KYCScorer
            passes_conf = conf_dec >= min_conf
            passes_outlier = (
                total_dec is not None and total_dec <= max_amt
            )
            will_be_used = passes_conf and passes_outlier and total_dec is not None

            print(
                f"  Will be used in KYC score: {will_be_used} "
                f"(passes_conf={passes_conf}, passes_outlier={passes_outlier})"
            )

            # Store the receipt in DB (raw model output)
            receipt = Receipt(
                user_id=user.id,
                file_name=img_path.name,
                file_path=str(img_path),
                status="completed",
                uploaded_at=datetime.utcnow(),
                company_name=company,
                receipt_date=r_date,
                receipt_address=parsed.get("receipt_address"),
                total_amount=total_dec,
                currency=currency,
                overall_confidence=conf_dec,
                confidence_company=conf_dec,
                confidence_date=conf_dec,
                confidence_address=conf_dec,
                confidence_total=conf_dec,
            )

            db.add(receipt)

        db.commit()

        # 4) Run KYC scoring
        scorer = KYCScorer(db)
        score = scorer.calculate_user_score(str(user.id))

        print(f"Final score:             {score.final_score}")
        print(f"Is verified:             {score.is_verified}")
        print(f"Document quality score:  {score.document_quality_score}")
        print(f"Spending pattern score:  {score.spending_pattern_score}")
        print(f"Consistency score:       {score.consistency_score}")
        print(f"Diversity score:         {score.diversity_score}")
        print(f"Total receipts (used):   {score.total_receipts}")
        print(f"Total spending (used):   {score.total_spending}")
        print(f"Unique companies:        {score.unique_companies}")
        print(f"Unique locations:        {score.unique_locations}")
        print(f"Date range (days):       {score.date_range_days}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
