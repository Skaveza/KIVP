# app/core/config.py
import os
from functools import lru_cache
from typing import List, Union

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    # ---------------------------------------------------------
    # Database / server config
    # ---------------------------------------------------------
    # Prefer env DATABASE_URL (Render/Oracle/Docker), fallback to localhost for dev
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/kyc_verification_db",
    )

    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ---------------------------------------------------------
    # JWT / auth
    # ---------------------------------------------------------
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")  # override in prod
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # ---------------------------------------------------------
    # File uploads
    # ---------------------------------------------------------
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(5_242_880)))  # 5 MB
    ALLOWED_EXTENSIONS: str = os.getenv(
        "ALLOWED_EXTENSIONS", "jpg,jpeg,png,pdf"
    )

    # ---------------------------------------------------------
    # API / project metadata
    # ---------------------------------------------------------
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    PROJECT_NAME: str = os.getenv(
        "PROJECT_NAME", "Kenyan KYC Verification Platform"
    )
    VERSION: str = os.getenv("VERSION", "1.0.0")
    DESCRIPTION: str = os.getenv(
        "DESCRIPTION", "Receipt-based KYC verification for Kenyan investors"
    )

    # CORS origins: allow either list or comma-separated string
    ALLOWED_ORIGINS: Union[str, List[str]] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:8080",
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # ---------------------------------------------------------
    # KYC scoring
    # ---------------------------------------------------------
    WEIGHT_DOCUMENT_QUALITY: float = float(os.getenv("WEIGHT_DOCUMENT_QUALITY", "0.30"))
    WEIGHT_SPENDING_PATTERN: float = float(os.getenv("WEIGHT_SPENDING_PATTERN", "0.25"))
    WEIGHT_CONSISTENCY: float = float(os.getenv("WEIGHT_CONSISTENCY", "0.25"))
    WEIGHT_DIVERSITY: float = float(os.getenv("WEIGHT_DIVERSITY", "0.20"))
    VERIFICATION_THRESHOLD: float = float(os.getenv("VERIFICATION_THRESHOLD", "75.0"))

    MIN_RECEIPT_CONFIDENCE: float = float(os.getenv("MIN_RECEIPT_CONFIDENCE", "0.95"))
    MAX_SINGLE_RECEIPT_KES: float = float(os.getenv("MAX_SINGLE_RECEIPT_KES", "200000.0"))

    # ---------------------------------------------------------
    # ML model config
    # ---------------------------------------------------------
    MODEL_PATH: str = os.getenv(
        "MODEL_PATH", "app/models/layoutlmv3_receipt_model/checkpoint-1000"
    )
    MODEL_DEVICE: str = os.getenv("MODEL_DEVICE", "cpu")
    MODEL_TYPE: str = os.getenv("MODEL_TYPE", "layoutlmv3")

    # ---------------------------------------------------------
    # pydantic-settings v2 config
    # - env_file is fine locally; Render/Oracle ignore it and use real env vars
    # ---------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
