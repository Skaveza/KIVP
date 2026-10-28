# Uwezo KYC: Receipt-Based Identity Verification

A research prototype testing whether receipts can serve as alternative evidence for KYC (know-your-customer) checks in Kenya, for people without formal credit histories. Built as a capstone project at African Leadership University.

## Status and limitations

- **Prototype only.** It is not suitable for real credit or onboarding decisions.
- **Model results.** A fine-tuned LayoutLMv3 scored a token-level macro F1 of 0.95 on the SROIE receipt benchmark. On synthetic Kenyan receipts it scored a macro F1 of 0.82 (370 labelled fields), with address, company and total at 1.00 but date extraction at only 0.26.
- **Not validated on real Kenyan receipts.** The synthetic data is very regular, so the Kenyan scores probably overstate real-world performance.
- **Scoring is hand-set.** The weights and verification threshold are configurable defaults, not calibrated against real verification outcomes.
- **Privacy.** Receipts and mobile money records are sensitive personal data. A real system would need consent, data minimisation and compliance with Kenya's Data Protection Act.
- **Hosting.** The API runs at https://uwezo.onrender.com (interactive docs at `/docs`). The React frontend is not currently deployed. The free tier can take up to a minute to wake.

## How it works

1. A user uploads a receipt (JPG, PNG or PDF).
2. OCR (Tesseract) and a fine-tuned LayoutLMv3 extract the merchant, date and amount. Low-confidence extractions are filtered out.
3. A scoring engine combines document quality (0.30), spending pattern (0.25), consistency over time (0.25) and transaction diversity (0.20) into a score, with a default verification threshold of 75.

## Tech stack

FastAPI, PostgreSQL (SQLAlchemy), JWT authentication, PyTorch and Hugging Face Transformers, Tesseract OCR, React (Vite), Docker, Render.

## Repository layout

- `kenyan-kyc-backend/` – FastAPI app, Dockerfile, `render.yaml`
- `kenyan-kyc-frontend/` – React frontend
- `LayoutMV3_.ipynb`, `Transfer_Learning_.ipynb` – training and evaluation notebooks
- `database_schema.sql` – database schema

## Run locally

Requires Python 3.11, PostgreSQL and Tesseract.

```bash
git clone https://github.com/Skaveza/KIVP.git
cd KIVP/kenyan-kyc-backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# create a .env with DATABASE_URL and SECRET_KEY
python create_db_tables.py
uvicorn app.main:app --reload
```

The fine-tuned checkpoint is downloaded from Hugging Face (`sifakaveza/layoutlm3_receipt_model`) by `app/scripts/download_model.py`. API docs are at http://localhost:8000/docs.

Frontend:

```bash
cd ../kenyan-kyc-frontend
npm install
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
npm run dev
```

Docker (backend):

```bash
cd kenyan-kyc-backend
docker build -t uwezo-kyc .
docker run -p 8000:8000 --env-file .env uwezo-kyc
```
