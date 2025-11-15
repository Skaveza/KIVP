"""
SQLAlchemy ORM Models
"""

from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class User(Base):
    """User/Investor Model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20))
    national_id = Column(String(50))
    
    kyc_status = Column(String(20), default='pending')
    kyc_score = Column(Numeric(5, 2), default=0.00)
    verification_date = Column(DateTime)
    
    account_type = Column(String(20), default='investor')
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    receipts = relationship("Receipt", back_populates="user", cascade="all, delete-orphan")
    verification_score = relationship("VerificationScore", back_populates="user", uselist=False)


class Receipt(Base):
    """Receipt Model"""
    __tablename__ = "receipts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    
    status = Column(String(20), default='pending', index=True)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    error_message = Column(Text)
    
    company_name = Column(String(255), index=True)
    receipt_date = Column(Date)
    receipt_address = Column(Text)
    total_amount = Column(Numeric(10, 2))
    currency = Column(String(3), default='KES')
    
    confidence_company = Column(Numeric(3, 2))
    confidence_date = Column(Numeric(3, 2))
    confidence_address = Column(Numeric(3, 2))
    confidence_total = Column(Numeric(3, 2))
    overall_confidence = Column(Numeric(3, 2))
    
    raw_extraction_json = Column(JSONB)
    
    uploaded_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="receipts")


class VerificationScore(Base):
    """Verification Score Model"""
    __tablename__ = "verification_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    
    document_quality_score = Column(Numeric(5, 2), default=0.00)
    spending_pattern_score = Column(Numeric(5, 2), default=0.00)
    consistency_score = Column(Numeric(5, 2), default=0.00)
    diversity_score = Column(Numeric(5, 2), default=0.00)
    final_score = Column(Numeric(5, 2), default=0.00, index=True)
    
    weight_document_quality = Column(Numeric(3, 2), default=0.30)
    weight_spending_pattern = Column(Numeric(3, 2), default=0.25)
    weight_consistency = Column(Numeric(3, 2), default=0.25)
    weight_diversity = Column(Numeric(3, 2), default=0.20)
    
    is_verified = Column(Boolean, default=False)
    verification_threshold = Column(Numeric(5, 2), default=75.00)
    
    total_receipts = Column(Integer, default=0)
    total_spending = Column(Numeric(12, 2), default=0.00)
    unique_companies = Column(Integer, default=0)
    unique_locations = Column(Integer, default=0)
    date_range_days = Column(Integer, default=0)
    average_transaction_amount = Column(Numeric(10, 2), default=0.00)
    
    calculated_at = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="verification_score")


class AuditLog(Base):
    """Audit Log Model"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), index=True)
    action_type = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    action_description = Column(Text)
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime, default=func.now(), index=True)
