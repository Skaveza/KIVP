"""
Configuration Settings
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 5242880
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Kenyan KYC Verification"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Receipt-based KYC verification"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # KYC Scoring
    WEIGHT_DOCUMENT_QUALITY: float = 0.30
    WEIGHT_SPENDING_PATTERN: float = 0.25
    WEIGHT_CONSISTENCY: float = 0.25
    WEIGHT_DIVERSITY: float = 0.20
    VERIFICATION_THRESHOLD: float = 75.00
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # ML Model
    MODEL_PATH: str = "./models/donut_model"
    MODEL_DEVICE: str = "cpu"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
