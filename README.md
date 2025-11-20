# Kenyan KYC Verification Platform (Uwezo Prototype)

This project is a **receipt-based KYC verification platform** for Kenyan investors.  
Users upload shopping/payment receipts, which are processed by a fine-tuned **LayoutLMv3** model to extract:

- Merchant / company name  
- Receipt date  
- Address  
- Total amount & currency  

These receipts are then aggregated into a **KYC score** based on document quality, spending patterns, consistency over time, and transaction diversity. The score helps assess whether a user should be verified for international investment platforms.

---

## Features

-  **JWT Authentication**
  - User registration & login with hashed passwords (Passlib + bcrypt)
  - Role support (e.g. `investor`, `admin`)

-  **Receipt Upload & Parsing**
  - Upload `.jpg`, `.jpeg`, `.png`, `.pdf` receipts
  - LayoutLMv3 model (via HuggingFace Transformers) with OCR enabled
  - Extracts company, date, address, total amount, currency
  - Stores full ML output in JSON for audit/debug

-  **KYC Scoring Engine**
  - Filters low-confidence or outlier receipts
  - Computes:
    - Document quality score
    - Spending pattern score
    - Consistency score
    - Diversity score
  - Weighted final KYC score with configurable thresholds
  - Updates user `kyc_status` (`pending`, `under_review`, `verified`)

-  **Dashboard & Analytics (API)**
  - Per-user:
    - Current KYC score & components
    - Receipts used vs dropped (with reasons)

---

## Tech Stack

**Backend**

- Python 3.11
- FastAPI (REST API)
- SQLAlchemy + PostgreSQL
- Pydantic / pydantic-settings
- Passlib (bcrypt) for password hashing
- Python-JOSE for JWT

**ML / OCR**

- HuggingFace Transformers (LayoutLMv3)
- PyTorch
- Tesseract OCR + PyTesseract
- Pillow

**Deployment**

- Uvicorn
- Docker (for containerization)
- Render (hosting)

---

## Project Structure (Key Folders)

```text
app/
  api/
    routes/
      auth.py          # register, login, current user
      receipts.py      # upload/list/delete receipts, file download
      verification.py  # KYC score, breakdown, requirements, history
  core/
    config.py          # settings (env-driven)
    database.py        # SQLAlchemy engine + SessionLocal
    security.py        # password hashing, JWT utilities
  models/
    models.py          # User, Receipt, VerificationScore, AuditLog
  schemas/
    schemas.py         # Pydantic models for requests & responses
  services/
    ml_service.py      # KYCModelService with LayoutLMv3
    kyc_scoring.py     # KYCScorer for KYC score calculation

models/
  layoutlmv3_receipt_model/
    checkpoint-1000/   # fine-tuned LayoutLMv3 weights & tokenizer (local)
```
## Setup & Local Development

### 1. Prerequisites

- Python **3.11**
- PostgreSQL (local or remote)
- Tesseract OCR installed on your machine  
  - macOS (Homebrew):
    ```bash
    brew install tesseract
    ```
- (Optional) `virtualenv` or `pyenv`

---

### 2. Clone the repository

```bash
git clone <your-repo-url>.git
cd kenyan-kyc-backend
```

### 3. Create and activate virtual environment
```bash
python3.11 -m venv venv
source venv/bin/activate   # macOS/Linux
# .\venv\Scripts\activate  # Windows (PowerShell)

```
### 4. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Make sure `requirements.txt` includes (at minimum):

```text
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
pydantic
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
python-multipart
transformers
torch
pillow
pytesseract
```


## 5 Environment Variables (`.env`)

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=postgresql://localhost:5432/kyc_verification_db

# JWT
SECRET_KEY=your-secret-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File uploads
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=5242880
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=Kenyan KYC Verification Platform
VERSION=1.0.0
DESCRIPTION=Receipt-based KYC verification for Kenyan investors

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080

# KYC scoring
WEIGHT_DOCUMENT_QUALITY=0.30
WEIGHT_SPENDING_PATTERN=0.25
WEIGHT_CONSISTENCY=0.25
WEIGHT_DIVERSITY=0.20
VERIFICATION_THRESHOLD=75.00

# Receipt filtering
MIN_RECEIPT_CONFIDENCE=0.95
MAX_SINGLE_RECEIPT_KES=100000

# ML model
MODEL_PATH=/app/models/layoutlmv3_receipt_model/checkpoint-1000
MODEL_DEVICE=cpu

# Environment
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

---

## 6. Create the Database

```bash
psql -U postgres -c "CREATE DATABASE kyc_verification_db;"
```

> If your app doesn't auto-create tables, run migrations or use `Base.metadata.create_all(...)`.

---

## 7. Run the Backend

```bash
uvicorn app.main:app --reload
```

---

## 8. API Documentation

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)  

---

## 9. Core API Endpoints

### Auth
```bash
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### Receipts
```bash
GET    /api/v1/receipts
POST   /api/v1/receipts/upload
GET    /api/v1/receipts/{id}/file
DELETE /api/v1/receipts/{id}
```

### Verification / KYC
```bash
GET  /api/v1/verification/score
POST /api/v1/verification/calculate
GET  /api/v1/verification/breakdown
GET  /api/v1/verification/history
GET  /api/v1/verification/requirements
```

---

## 10. Admin (Optional)
```bash
GET /api/v1/admin/users
GET /api/v1/admin/logs
POST /api/v1/admin/model/reload
```

---

## 11. Docker (Optional)

### Build Image
```bash
docker build -t kyc-backend .
```

### Run Container
```bash
docker run -p 8000:8000 --env-file .env kyc-backend
```


