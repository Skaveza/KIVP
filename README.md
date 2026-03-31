# Uwezo KYC - Receipt Based I dentity Verification Platform
[Demo Video]{https://youtu.be/wmPyv_Fk1E8}

Uwezo KYC is a backend system that enables identity verification using alternative financial data (receipts).

Users upload receipts, which are processed using a fine-tuned LayoutLMv3 model to extract structured data.

This data is aggregated into a KYC score used to assess eligibility for financial services.

---

## Tech Stack

**Backend**

- Python (FastAPI)
- PostgreSQL (SQLAlchemy ORM)
- JWT Authentication (python-jose, passlib)

**Machine Learning**

- LayoutLMv3 (HuggingFace Transformers)
- PyTorch
- Tesseract OCR

**Deployment**

- Uvicorn
- Docker
- Render

---

## Features

 **Authentication**
-JWT-based authentication
-Secure password hashing (bcrypt)
-Role-based access (user/admin)

 **Receipt Processing**
- Upload receipts (JPG, PNG, PDF)
- OCR + LayoutLMv3 extraction
- Structured output (merchant, date, amount, etc.)
-  Confidence-based filtering

   **KYC Scoring Engine**
-  Multi-factor scoring:
     - Document quality
     - Spending patterns
     - Consistency over time
     - Transaction diversity
- Configurable weights and thresholds
- Automatic verification status updates

  **Analytics (API)**
- User dashboard with aggregated metrics
- Receipt usage tracking (used vs dropped)
- Spending analysis by company
- Score breakdown and history

---
## API Endpoints

### Auth
```bash
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### Users
```bash
GET   /api/v1/users/profile
PATCH /api/v1/users/profile
GET   /api/v1/users/dashboard
GET   /api/v1/users/stats
```

### Receipts
```bash
POST   /api/v1/receipts/upload
GET    /api/v1/receipts
DELETE /api/v1/receipts/{id}
```

## Verification
```bash
GET  /api/v1/verification/score
POST /api/v1/verification/calculate
GET  /api/v1/verification/breakdown
GET  /api/v1/verification/history
```

---

## Run Locally
   ```bash
    git clone https://github.com/Skaveza/KIVP.git
    cd KIVP
    pip install -r requirements.txt
    uvicorn app.main:app --reload
   ```

---

## Run with Docker

```bash
docker build -t uwezo-kyc .
docker run -p 8000:8000 --env-file .env uwezo-kyc
```
