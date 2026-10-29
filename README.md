# Uwezo KYC: Receipt-Based Identity Verification

A research prototype testing whether receipts can serve as alternative evidence for KYC (know-your-customer) checks in Kenya, for people without formal credit histories. Built as a capstone project at African Leadership University.

**Live site:** https://uwezo-pujl.onrender.com · **API docs:** https://uwezo.onrender.com/docs

## Status and limitations

- **Prototype only.** It is not suitable for real credit or onboarding decisions.
- **Model results.** A fine-tuned LayoutLMv3 scored a token-level macro F1 of 0.95 on the SROIE receipt benchmark. On synthetic Kenyan receipts it scored a macro F1 of 0.82 (370 labelled fields), with address, company and total at 1.00 but date extraction at only 0.26.
- **Not validated on real Kenyan receipts.** The synthetic data is very regular, so the Kenyan scores probably overstate real-world performance. Because dates are read least reliably, the consistency signal is the least dependable.
- **Scoring is hand-set.** The weights and verification threshold are configurable defaults, not calibrated against real verification outcomes.
- **Privacy.** Receipts and mobile money records are sensitive personal data. A real system would need consent, data minimisation and compliance with Kenya's Data Protection Act. Please upload sample receipts only.
- **Hosting.** The frontend and API both run on Render's free tier, so the first request after a quiet period can take up to a minute.

## How it works

1. **Upload.** A user uploads a receipt (JPG, PNG or PDF, up to 5MB).
2. **Read.** OCR (Tesseract) and a fine-tuned LayoutLMv3 extract the merchant, address, date and total.
3. **Filter.** Receipts with a missing merchant, low model confidence or an unusual total are set aside.
4. **Score.** The remaining receipts are scored out of 100 and combined using these weights. At 75 or above, the profile counts as verified.

| Signal | Weight | What it measures |
|---|---|---|
| Document quality | 0.30 | How confidently the model read each receipt |
| Spending pattern | 0.25 | Amount spent and number of receipts, weighted by confidence in the totals |
| Consistency | 0.25 | How regularly receipts appear over time, using the dates read |
| Diversity | 0.20 | Number of different merchants and locations |

## Tech stack

FastAPI, PostgreSQL (SQLAlchemy), JWT authentication, PyTorch and Hugging Face Transformers, Tesseract OCR, React (Vite, Tailwind CSS), Docker, Render.

## Repository layout

- `kenyan-kyc-backend/`: FastAPI app, Dockerfile, `render.yaml`, `.env.example`
- `kenyan-kyc-frontend/`: React frontend
- `LayoutMV3_.ipynb`, `Transfer_Learning_.ipynb`: training and evaluation notebooks
- `database_schema.sql`: database schema

## Run locally

Requires Python 3.11, PostgreSQL and Tesseract.

```bash
git clone https://github.com/Skaveza/KIVP.git
cd KIVP/kenyan-kyc-backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set DATABASE_URL and SECRET_KEY
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
