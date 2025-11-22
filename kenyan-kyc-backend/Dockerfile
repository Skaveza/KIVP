FROM python:3.11-slim

# Environment settings 
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_PATH=/app/models/layoutlmv3_receipt_model/checkpoint-1000 \
    MODEL_DEVICE=cpu

#  System deps (Tesseract + build tools + Postgres client libs) 
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory 
WORKDIR /app

# Install Python deps first 
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy model into image 
COPY app/models/layoutlmv3_receipt_model /app/models/layoutlmv3_receipt_model

#  Copy the rest of the codebase 
COPY . .

# Ensure uploads directory exists
RUN mkdir -p /app/uploads

#  Expose FastAPI port 
EXPOSE 8000

# Start app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
