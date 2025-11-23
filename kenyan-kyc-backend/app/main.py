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
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs"
)

allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting application...")
    if check_db_connection():
        logger.info("Database connected")
    else:
        logger.error("Database failed!")

@app.get("/")
def root():
    return {"status": "running", "docs": "/docs"}

@app.get("/health")
def health():
    db_status = "connected" if check_db_connection() else "disconnected"
    return {"status": "healthy", "database": db_status}

# Routes
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(receipts.router, prefix=settings.API_V1_PREFIX)
app.include_router(verification.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
