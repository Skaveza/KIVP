"""
Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import check_db_connection
from app.api.routes import auth, users, receipts, verification, admin
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kenyan KYC Verification Platform",
    version="1.0.0",
    description="Receipt-based KYC verification",
    docs_url="/docs"
)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info(" Starting application...")
    if check_db_connection():
        logger.info(" Database connected")
    else:
        logger.error(" Database failed!")

@app.get("/")
def root():
    return {"status": "running", "docs": "/docs"}

@app.get("/health")
def health_check():
    db_status = "connected" if check_db_connection() else "disconnected"
    return {"status": "healthy", "database": db_status}

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(receipts.router, prefix="/api/v1")
app.include_router(verification.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
