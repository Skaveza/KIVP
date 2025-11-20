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


