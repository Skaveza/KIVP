# reset_test_data.py
from app.core.database import SessionLocal
from app.models.models import Receipt, VerificationScore, User

def main():
    db = SessionLocal()

    # pick the test user email
    user = db.query(User).filter(User.email == "user4@example.com").first()
    if not user:
        print("Test user not found")
        return

    # delete receipts
    db.query(Receipt).filter(Receipt.user_id == user.id).delete()

    # delete verification score
    db.query(VerificationScore).filter(VerificationScore.user_id == user.id).delete()

    # reset KYC fields on user
    user.kyc_score = 0
    user.kyc_status = "pending"
    user.verification_date = None

    db.commit()
    print(" Reset receipts and scores for", user.email)

if __name__ == "__main__":
    main()
