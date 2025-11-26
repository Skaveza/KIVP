FROM python:3.11-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_PATH=/app/models/layoutlmv3_receipt_model/checkpoint-1000 \
    MODEL_DEVICE=cpu \
    HF_HOME=/app/.cache/huggingface

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-osd \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the codebase
COPY . .

# Download HF model at build time (repo is public)
ARG HF_MODEL_REPO=sifakaveza/layoutlm3_receipt_model
ARG HF_MODEL_SUBFOLDER=checkpoint-1000
ENV HF_MODEL_REPO=$HF_MODEL_REPO
ENV HF_MODEL_SUBFOLDER=$HF_MODEL_SUBFOLDER

RUN python app/scripts/download_model.py && \
    mkdir -p /app/uploads

    COPY startup.sh .
    RUN chmod +x startup.sh
    
    EXPOSE 8000
    
    CMD ["./startup.sh"]
