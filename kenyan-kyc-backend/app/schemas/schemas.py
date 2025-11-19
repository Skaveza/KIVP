"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID as UUID_Type


# -----------------------------
# User Schemas
# -----------------------------
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    national_id: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    kyc_status: str
    kyc_score: Decimal
    account_type: str
    is_active: bool
    created_at: datetime
    verification_date: Optional[datetime] = None

    @field_validator('id', mode='before')
    def convert_uuid_to_str(cls, v):
        return str(v) if isinstance(v, UUID_Type) else v

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    national_id: Optional[str] = None


# -----------------------------
# Receipt Schemas
# -----------------------------
class ReceiptResponse(BaseModel):
    id: str
    user_id: str
    file_name: str
    file_path: str
    status: str
    company_name: Optional[str] = None
    receipt_date: Optional[date] = None
    receipt_address: Optional[str] = None
    total_amount: Optional[Decimal] = None
    currency: str = 'KES'
    overall_confidence: Optional[Decimal] = None
    accuracy: Optional[float] = None  # <-- ADDED
    uploaded_at: datetime
    error_message: Optional[str] = None

    @field_validator('id', 'user_id', mode='before')
    def convert_uuid_to_str(cls, v):
        return str(v) if isinstance(v, UUID_Type) else v

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Verification Score Schemas
# -----------------------------
class VerificationScoreResponse(BaseModel):
    user_id: str
    document_quality_score: Decimal
    spending_pattern_score: Decimal
    consistency_score: Decimal
    diversity_score: Decimal
    final_score: Decimal
    is_verified: bool
    total_receipts: int
    total_spending: Decimal
    unique_companies: int
    unique_locations: int
    date_range_days: int
    calculated_at: datetime
    average_transaction_amount: Decimal
    model_accuracy: Optional[float] = None  # <-- ADDED

    @field_validator('user_id', mode='before')
    def convert_uuid_to_str(cls, v):
        return str(v) if isinstance(v, UUID_Type) else v

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Dashboard Schema
# -----------------------------
class UserDashboard(BaseModel):
    user: UserResponse
    verification_score: Optional[VerificationScoreResponse] = None
    recent_receipts: List[ReceiptResponse]
    total_receipts: int
    processed_receipts: int
    pending_receipts: int


# -----------------------------
# Admin Statistics Schema
# -----------------------------
class AdminStatistics(BaseModel):
    total_users: int
    verified_users: int
    pending_users: int
    under_review_users: int
    total_receipts: int
    processed_receipts: int
    failed_receipts: int
    total_platform_spending: Decimal
    average_kyc_score: Decimal


# -----------------------------
# Authentication Schemas
# -----------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str
    email: str
    account_type: str


# -----------------------------
# Generic
# -----------------------------
class MessageResponse(BaseModel):
    message: str
    success: bool = True
