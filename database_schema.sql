-- =====================================================
-- KENYAN INVESTOR KYC VERIFICATION PLATFORM
-- Database Schema for PostgreSQL
-- =====================================================

-- Enable UUID extension for generating unique IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. USERS TABLE (Investors)
-- =====================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    national_id VARCHAR(50), -- Kenyan National ID
    
    -- KYC Status
    kyc_status VARCHAR(20) DEFAULT 'pending' CHECK (kyc_status IN ('pending', 'verified', 'rejected', 'under_review')),
    kyc_score DECIMAL(5,2) DEFAULT 0.00, -- Current KYC score (0-100)
    verification_date TIMESTAMP,
    
    -- Account Info
    account_type VARCHAR(20) DEFAULT 'investor' CHECK (account_type IN ('investor', 'admin')),
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Indexes
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Indexes for users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_kyc_status ON users(kyc_status);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- =====================================================
-- 2. RECEIPTS TABLE (Uploaded Images & Metadata)
-- =====================================================
CREATE TABLE receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- File Information
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL, -- Storage path (local/S3/etc)
    file_size INTEGER, -- Size in bytes
    file_type VARCHAR(50), -- image/jpeg, image/png, etc
    
    -- Processing Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    error_message TEXT,
    
    -- Extracted Data (from ML model)
    company_name VARCHAR(255),
    receipt_date DATE,
    receipt_address TEXT,
    total_amount DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'KES', -- Kenyan Shilling
    
    -- Extraction Confidence Scores (0-1)
    confidence_company DECIMAL(3,2),
    confidence_date DECIMAL(3,2),
    confidence_address DECIMAL(3,2),
    confidence_total DECIMAL(3,2),
    overall_confidence DECIMAL(3,2), -- Average confidence
    
    -- Additional Data
    raw_extraction_json JSONB, -- Full ML model output
    
    -- Metadata
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_amount CHECK (total_amount >= 0)
);

-- Indexes for receipts table
CREATE INDEX idx_receipts_user_id ON receipts(user_id);
CREATE INDEX idx_receipts_status ON receipts(status);
CREATE INDEX idx_receipts_receipt_date ON receipts(receipt_date DESC);
CREATE INDEX idx_receipts_uploaded_at ON receipts(uploaded_at DESC);
CREATE INDEX idx_receipts_company_name ON receipts(company_name);
CREATE INDEX idx_receipts_extraction_json ON receipts USING GIN (raw_extraction_json);

-- =====================================================
-- 3. VERIFICATION_SCORES TABLE (KYC Score Components)
-- =====================================================
CREATE TABLE verification_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Score Components (0-100 each)
    document_quality_score DECIMAL(5,2) DEFAULT 0.00, -- Based on extraction confidence
    spending_pattern_score DECIMAL(5,2) DEFAULT 0.00, -- Total amount & frequency
    consistency_score DECIMAL(5,2) DEFAULT 0.00, -- Regular transactions over time
    diversity_score DECIMAL(5,2) DEFAULT 0.00, -- Different businesses/locations
    
    -- Weighted Final Score
    final_score DECIMAL(5,2) DEFAULT 0.00, -- Weighted average (0-100)
    
    -- Score Weights (must sum to 1.0)
    weight_document_quality DECIMAL(3,2) DEFAULT 0.30,
    weight_spending_pattern DECIMAL(3,2) DEFAULT 0.25,
    weight_consistency DECIMAL(3,2) DEFAULT 0.25,
    weight_diversity DECIMAL(3,2) DEFAULT 0.20,
    
    -- Verification Decision
    is_verified BOOLEAN DEFAULT false, -- True if final_score >= 75
    verification_threshold DECIMAL(5,2) DEFAULT 75.00,
    
    -- Supporting Metrics
    total_receipts INTEGER DEFAULT 0,
    total_spending DECIMAL(12,2) DEFAULT 0.00,
    unique_companies INTEGER DEFAULT 0,
    unique_locations INTEGER DEFAULT 0,
    date_range_days INTEGER DEFAULT 0, -- Days between first and last receipt
    average_transaction_amount DECIMAL(10,2) DEFAULT 0.00,
    
    -- Metadata
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_scores CHECK (
        document_quality_score BETWEEN 0 AND 100 AND
        spending_pattern_score BETWEEN 0 AND 100 AND
        consistency_score BETWEEN 0 AND 100 AND
        diversity_score BETWEEN 0 AND 100 AND
        final_score BETWEEN 0 AND 100
    ),
    CONSTRAINT valid_weights CHECK (
        weight_document_quality + weight_spending_pattern + 
        weight_consistency + weight_diversity = 1.0
    )
);

-- Indexes for verification_scores table
CREATE INDEX idx_verification_scores_user_id ON verification_scores(user_id);
CREATE INDEX idx_verification_scores_final_score ON verification_scores(final_score DESC);
CREATE INDEX idx_verification_scores_calculated_at ON verification_scores(calculated_at DESC);

-- Unique constraint: One score record per user (latest calculation)
CREATE UNIQUE INDEX idx_verification_scores_user_latest ON verification_scores(user_id);

-- =====================================================
-- 4. AUDIT_LOGS TABLE (System Actions & Changes)
-- =====================================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Who & What
    user_id UUID REFERENCES users(id) ON DELETE SET NULL, -- NULL if system action
    action_type VARCHAR(50) NOT NULL, -- 'user_created', 'receipt_uploaded', 'score_calculated', etc
    entity_type VARCHAR(50), -- 'user', 'receipt', 'score', etc
    entity_id UUID, -- ID of the affected entity
    
    -- Action Details
    action_description TEXT,
    old_value JSONB, -- Previous state (for updates)
    new_value JSONB, -- New state
    
    -- Request Context
    ip_address INET,
    user_agent TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes inline for performance
    CONSTRAINT valid_action_type CHECK (action_type IN (
        'user_registered', 'user_login', 'user_updated', 'user_deleted',
        'receipt_uploaded', 'receipt_processed', 'receipt_failed', 'receipt_deleted',
        'score_calculated', 'verification_status_changed',
        'admin_action', 'system_action'
    ))
);

-- Indexes for audit_logs table
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX idx_audit_logs_entity_type_id ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- =====================================================
-- 5. VERIFICATION_HISTORY TABLE (Score Changes Over Time)
-- =====================================================
-- Track how scores evolve as users upload more receipts
CREATE TABLE verification_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Snapshot of scores at this point in time
    document_quality_score DECIMAL(5,2),
    spending_pattern_score DECIMAL(5,2),
    consistency_score DECIMAL(5,2),
    diversity_score DECIMAL(5,2),
    final_score DECIMAL(5,2),
    
    -- Context
    total_receipts_at_time INTEGER,
    trigger_event VARCHAR(50), -- 'receipt_added', 'manual_recalculation', etc
    
    -- Metadata
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for verification_history table
CREATE INDEX idx_verification_history_user_id ON verification_history(user_id);
CREATE INDEX idx_verification_history_recorded_at ON verification_history(recorded_at DESC);

-- =====================================================
-- TRIGGERS & FUNCTIONS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for receipts table
CREATE TRIGGER update_receipts_updated_at
    BEFORE UPDATE ON receipts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically log score history
CREATE OR REPLACE FUNCTION log_score_to_history()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO verification_history (
        user_id, 
        document_quality_score,
        spending_pattern_score,
        consistency_score,
        diversity_score,
        final_score,
        total_receipts_at_time,
        trigger_event
    ) VALUES (
        NEW.user_id,
        NEW.document_quality_score,
        NEW.spending_pattern_score,
        NEW.consistency_score,
        NEW.diversity_score,
        NEW.final_score,
        NEW.total_receipts,
        'score_updated'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to log score changes
CREATE TRIGGER log_verification_score_changes
    AFTER INSERT OR UPDATE ON verification_scores
    FOR EACH ROW
    EXECUTE FUNCTION log_score_to_history();

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View: User Dashboard Summary
CREATE OR REPLACE VIEW user_dashboard_summary AS
SELECT 
    u.id as user_id,
    u.full_name,
    u.email,
    u.kyc_status,
    u.kyc_score,
    COUNT(r.id) as total_receipts,
    COUNT(CASE WHEN r.status = 'completed' THEN 1 END) as processed_receipts,
    COUNT(CASE WHEN r.status = 'failed' THEN 1 END) as failed_receipts,
    SUM(r.total_amount) as total_spending,
    MAX(r.uploaded_at) as last_upload_date,
    vs.final_score,
    vs.is_verified
FROM users u
LEFT JOIN receipts r ON u.id = r.user_id
LEFT JOIN verification_scores vs ON u.id = vs.user_id
GROUP BY u.id, u.full_name, u.email, u.kyc_status, u.kyc_score, vs.final_score, vs.is_verified;

-- View: Admin Statistics
CREATE OR REPLACE VIEW admin_statistics AS
SELECT 
    COUNT(DISTINCT u.id) as total_users,
    COUNT(DISTINCT CASE WHEN u.kyc_status = 'verified' THEN u.id END) as verified_users,
    COUNT(DISTINCT CASE WHEN u.kyc_status = 'pending' THEN u.id END) as pending_users,
    COUNT(r.id) as total_receipts,
    COUNT(CASE WHEN r.status = 'completed' THEN 1 END) as processed_receipts,
    SUM(r.total_amount) as total_platform_spending,
    AVG(vs.final_score) as average_kyc_score,
    COUNT(DISTINCT r.company_name) as unique_companies
FROM users u
LEFT JOIN receipts r ON u.id = r.user_id
LEFT JOIN verification_scores vs ON u.id = vs.user_id;

-- View: Recent Activity Feed
CREATE OR REPLACE VIEW recent_activity AS
SELECT 
    al.id,
    al.action_type,
    al.action_description,
    al.created_at,
    u.full_name as user_name,
    u.email as user_email
FROM audit_logs al
LEFT JOIN users u ON al.user_id = u.id
ORDER BY al.created_at DESC
LIMIT 50;

-- =====================================================
-- SEED DATA (For Demo/Testing)
-- =====================================================

-- Insert demo admin user (password: 'admin123' - hash this in production!)
INSERT INTO users (email, password_hash, full_name, phone_number, account_type, kyc_status, kyc_score)
VALUES 
    ('admin@kenyakyc.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5i.q5n0P.V3bS', 'Admin User', '+254712345678', 'admin', 'verified', 100.00);

-- Insert demo investor users
INSERT INTO users (email, password_hash, full_name, phone_number, national_id, kyc_status, kyc_score)
VALUES 
    ('john.doe@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5i.q5n0P.V3bS', 'John Doe', '+254723456789', '12345678', 'verified', 85.50),
    ('jane.smith@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5i.q5n0P.V3bS', 'Jane Smith', '+254734567890', '23456789', 'pending', 45.20),
    ('alex.kamau@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5i.q5n0P.V3bS', 'Alex Kamau', '+254745678901', '34567890', 'under_review', 72.80);

