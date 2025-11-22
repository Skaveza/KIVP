"""
Database Connection and Session Management
"""

import os
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool

from app.core.config import settings


def _normalize_db_url(url: str) -> str:
    """
    Normalize common provider URLs.
    - Convert postgres:// to postgresql:// for SQLAlchemy compatibility.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


DATABASE_URL = _normalize_db_url(settings.DATABASE_URL)

# Optional SSL enforcement (Render/Oracle often need this)
# You can set DB_SSL=require in Render env vars, or include sslmode in DATABASE_URL.
DB_SSL = os.getenv("DB_SSL", "").lower()  # e.g., "require"

connect_args = {}
if DB_SSL == "require" and "sslmode=" not in DATABASE_URL:
    connect_args["sslmode"] = "require"

# Pool settings can be overridden by env vars in prod
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=POOL_RECYCLE,
    echo=settings.DEBUG,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Check if database connection is working"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
