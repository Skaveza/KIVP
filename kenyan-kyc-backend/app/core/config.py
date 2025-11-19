from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Database / server config
    DATABASE_URL: str = "postgresql://localhost:5432/kyc_verification_db"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # JWT / auth 
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # File uploads 
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 5_242_880  # 5 MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf"

    # API / project metadata
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Kenyan KYC Verification Platform"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Receipt-based KYC verification for Kenyan investors"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"

    # KYC scoring
    WEIGHT_DOCUMENT_QUALITY: float = 0.30
    WEIGHT_SPENDING_PATTERN: float = 0.25
    WEIGHT_CONSISTENCY: float = 0.25
    WEIGHT_DIVERSITY: float = 0.20
    VERIFICATION_THRESHOLD: float = 75.0

    # 🔐 KYC receipt filters
    MIN_RECEIPT_CONFIDENCE: float = 0.95
    MAX_SINGLE_RECEIPT_KES: float = 200_000.0  

    # ML model config 
    MODEL_PATH: str = "/Volumes/Peach/layoutlmv3_receipt_model/checkpoint-1000"
    MODEL_DEVICE: str = "cpu"
    MODEL_TYPE: str = "layoutlmv3"

    # pydantic-settings v2 style
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
