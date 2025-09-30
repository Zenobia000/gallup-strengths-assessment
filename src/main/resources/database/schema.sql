-- =============================================================================
-- Gallup Strengths Assessment System - Complete Database Schema
-- =============================================================================
-- This schema supports psychological assessments with full compliance features:
-- - 24-hour TTL for sensitive data
-- - GDPR compliance with audit trails
-- - Data anonymization and consent management
-- - Session isolation and data integrity
-- =============================================================================

-- Enable foreign key constraints and WAL mode
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 30000;

-- =============================================================================
-- CORE ASSESSMENT TABLES
-- =============================================================================

-- Assessment Sessions - Core session management with TTL
CREATE TABLE assessment_sessions (
    session_id TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK (status IN ('created', 'active', 'completed', 'expired', 'abandoned')),
    participant_type TEXT NOT NULL CHECK (participant_type IN ('individual', 'team_member', 'leader', 'student')),
    language TEXT NOT NULL DEFAULT 'en',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, '+24 hours')),
    last_activity_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    metadata TEXT, -- JSON for flexible session data
    ip_address_hash TEXT, -- Anonymized IP for compliance
    user_agent_hash TEXT, -- Anonymized user agent
    timezone TEXT
);

-- Consent Records - GDPR compliance and consent tracking
CREATE TABLE consent_records (
    consent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    consent_types TEXT NOT NULL, -- JSON array of consent types
    consent_given BOOLEAN NOT NULL DEFAULT TRUE,
    consent_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address_hash TEXT, -- Anonymized IP
    user_agent_hash TEXT, -- Anonymized user agent
    ttl_expires_at DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, '+24 hours')),
    legal_basis TEXT, -- GDPR legal basis
    consent_version TEXT NOT NULL DEFAULT '1.0',
    withdrawal_timestamp DATETIME,

    FOREIGN KEY (session_id) REFERENCES assessment_sessions(session_id) ON DELETE CASCADE
);

-- Assessment Responses - Individual question responses with TTL
CREATE TABLE assessment_responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question_id INTEGER NOT NULL,
    selected_value INTEGER NOT NULL,
    response_time_ms INTEGER, -- Time taken to answer
    confidence_level INTEGER, -- 1-5 scale
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ttl_expires_at DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, '+24 hours')),
    sequence_number INTEGER, -- Order in assessment

    FOREIGN KEY (session_id) REFERENCES assessment_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id),
    UNIQUE(session_id, question_id) -- Prevent duplicate responses
);

-- Strength Scores - Calculated assessment results
CREATE TABLE strength_scores (
    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    strength_name TEXT NOT NULL,
    theme TEXT NOT NULL,
    score REAL NOT NULL,
    percentile REAL,
    rank_position INTEGER, -- 1-34 ranking
    calculation_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    calculation_metadata TEXT, -- JSON with algorithm details
    confidence_interval_lower REAL,
    confidence_interval_upper REAL,
    ttl_expires_at DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, '+24 hours')),

    FOREIGN KEY (session_id) REFERENCES assessment_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (strength_name) REFERENCES gallup_strengths(strength_name),
    UNIQUE(session_id, strength_name) -- One score per strength per session
);

-- =============================================================================
-- AUDIT AND COMPLIANCE TABLES
-- =============================================================================

-- Audit Trails - Complete operation tracking for compliance
CREATE TABLE audit_trails (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    action_type TEXT NOT NULL CHECK (action_type IN (
        'session_created', 'consent_given', 'consent_withdrawn', 'assessment_started',
        'question_answered', 'assessment_completed', 'data_accessed', 'data_updated',
        'data_deleted', 'privacy_request', 'data_export', 'session_expired', 'data_created'
    )),
    entity_type TEXT NOT NULL CHECK (entity_type IN (
        'session', 'consent', 'response', 'score', 'question', 'user_data', 'system'
    )),
    entity_id TEXT,
    old_values TEXT, -- JSON of previous state
    new_values TEXT, -- JSON of new state
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address_hash TEXT, -- Anonymized IP
    user_agent_hash TEXT, -- Anonymized user agent
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT
);

-- Privacy Requests - GDPR subject access requests
CREATE TABLE privacy_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    request_type TEXT NOT NULL CHECK (request_type IN (
        'data_export', 'data_deletion', 'data_correction', 'processing_restriction'
    )),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'processing', 'completed', 'rejected'
    )),
    request_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_timestamp DATETIME,
    requester_verification TEXT, -- How identity was verified
    processing_notes TEXT,

    FOREIGN KEY (session_id) REFERENCES assessment_sessions(session_id)
);

-- =============================================================================
-- REFERENCE DATA TABLES
-- =============================================================================

-- Gallup Strengths - 34 strength themes with detailed descriptions
CREATE TABLE gallup_strengths (
    strength_id INTEGER PRIMARY KEY AUTOINCREMENT,
    strength_name TEXT NOT NULL UNIQUE,
    theme TEXT NOT NULL CHECK (theme IN (
        'Executing', 'Influencing', 'Relationship Building', 'Strategic Thinking'
    )),
    description TEXT NOT NULL,
    key_characteristics TEXT, -- JSON array
    development_suggestions TEXT, -- JSON array
    related_strengths TEXT, -- JSON array
    complementary_strengths TEXT, -- JSON array
    potential_blind_spots TEXT, -- JSON array
    leadership_application TEXT,
    team_contribution TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Questions - Mini-IPIP and assessment question bank
CREATE TABLE questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL CHECK (question_type IN (
        'likert_5', 'likert_7', 'binary', 'ranking', 'multiple_choice'
    )),
    theme_mapping TEXT, -- JSON mapping to strength themes
    scoring_key TEXT NOT NULL, -- JSON with scoring instructions
    language TEXT NOT NULL DEFAULT 'en',
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    estimated_time_seconds INTEGER DEFAULT 30,
    question_category TEXT,
    reverse_scored BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

-- Assessment Configurations - Different assessment types and settings
CREATE TABLE assessment_configurations (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_name TEXT NOT NULL UNIQUE,
    assessment_type TEXT NOT NULL CHECK (assessment_type IN (
        'full_assessment', 'quick_assessment', 'team_assessment', 'leadership_assessment'
    )),
    question_count INTEGER NOT NULL,
    time_limit_minutes INTEGER,
    randomize_questions BOOLEAN DEFAULT TRUE,
    require_all_questions BOOLEAN DEFAULT TRUE,
    scoring_algorithm TEXT NOT NULL, -- JSON configuration
    result_categories TEXT, -- JSON array
    active BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Question Sets - Links assessments to questions
CREATE TABLE question_sets (
    set_id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    sequence_order INTEGER NOT NULL,
    weight REAL DEFAULT 1.0,
    required BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (config_id) REFERENCES assessment_configurations(config_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id),
    UNIQUE(config_id, question_id) -- No duplicate questions in same config
);

-- =============================================================================
-- DATA RETENTION AND TTL TRIGGERS
-- =============================================================================

-- Trigger to automatically update last_activity_at on session updates
CREATE TRIGGER update_session_activity
    AFTER UPDATE ON assessment_sessions
    FOR EACH ROW
    WHEN OLD.status != NEW.status OR OLD.metadata != NEW.metadata
BEGIN
    UPDATE assessment_sessions
    SET last_activity_at = CURRENT_TIMESTAMP
    WHERE session_id = NEW.session_id;
END;

-- Trigger to create audit trail for session changes
CREATE TRIGGER audit_session_changes
    AFTER UPDATE ON assessment_sessions
    FOR EACH ROW
BEGIN
    INSERT INTO audit_trails (
        session_id, action_type, entity_type, entity_id,
        old_values, new_values, timestamp
    ) VALUES (
        NEW.session_id, 'data_updated', 'session', NEW.session_id,
        json_object(
            'status', OLD.status,
            'last_activity_at', OLD.last_activity_at,
            'metadata', OLD.metadata
        ),
        json_object(
            'status', NEW.status,
            'last_activity_at', NEW.last_activity_at,
            'metadata', NEW.metadata
        ),
        CURRENT_TIMESTAMP
    );
END;

-- Trigger to create audit trail for new responses
CREATE TRIGGER audit_new_response
    AFTER INSERT ON assessment_responses
    FOR EACH ROW
BEGIN
    INSERT INTO audit_trails (
        session_id, action_type, entity_type, entity_id,
        new_values, timestamp
    ) VALUES (
        NEW.session_id, 'question_answered', 'response', NEW.response_id,
        json_object(
            'question_id', NEW.question_id,
            'selected_value', NEW.selected_value,
            'response_time_ms', NEW.response_time_ms,
            'confidence_level', NEW.confidence_level
        ),
        CURRENT_TIMESTAMP
    );
END;

-- Trigger to audit consent records
CREATE TRIGGER audit_consent_records
    AFTER INSERT ON consent_records
    FOR EACH ROW
BEGIN
    INSERT INTO audit_trails (
        session_id, action_type, entity_type, entity_id,
        new_values, timestamp
    ) VALUES (
        NEW.session_id, 'consent_given', 'consent', NEW.consent_id,
        json_object(
            'consent_types', NEW.consent_types,
            'consent_version', NEW.consent_version,
            'legal_basis', NEW.legal_basis
        ),
        CURRENT_TIMESTAMP
    );
END;

-- Trigger to update timestamps on gallup_strengths updates
CREATE TRIGGER update_strength_timestamp
    AFTER UPDATE ON gallup_strengths
    FOR EACH ROW
BEGIN
    UPDATE gallup_strengths
    SET updated_at = CURRENT_TIMESTAMP
    WHERE strength_id = NEW.strength_id;
END;

-- Trigger to update timestamps on questions updates
CREATE TRIGGER update_question_timestamp
    AFTER UPDATE ON questions
    FOR EACH ROW
BEGIN
    UPDATE questions
    SET updated_at = CURRENT_TIMESTAMP
    WHERE question_id = NEW.question_id;
END;

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- View for active sessions with consent status
CREATE VIEW active_sessions_with_consent AS
SELECT
    s.session_id,
    s.status,
    s.participant_type,
    s.created_at,
    s.expires_at,
    s.last_activity_at,
    CASE WHEN c.consent_id IS NOT NULL THEN TRUE ELSE FALSE END as has_consent,
    c.consent_types,
    c.consent_timestamp
FROM assessment_sessions s
LEFT JOIN consent_records c ON s.session_id = c.session_id
    AND c.withdrawal_timestamp IS NULL
WHERE s.status IN ('active', 'created')
    AND s.expires_at > CURRENT_TIMESTAMP;

-- View for session completion statistics
CREATE VIEW session_completion_stats AS
SELECT
    DATE(created_at) as assessment_date,
    COUNT(*) as total_sessions,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
    COUNT(CASE WHEN status = 'abandoned' THEN 1 END) as abandoned_sessions,
    COUNT(CASE WHEN status = 'expired' THEN 1 END) as expired_sessions,
    ROUND(
        COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*), 2
    ) as completion_rate
FROM assessment_sessions
GROUP BY DATE(created_at)
ORDER BY assessment_date DESC;

-- View for strength distribution analysis
CREATE VIEW strength_distribution AS
SELECT
    s.strength_name,
    s.theme,
    COUNT(*) as assessment_count,
    ROUND(AVG(s.score), 2) as avg_score,
    ROUND(MIN(s.score), 2) as min_score,
    ROUND(MAX(s.score), 2) as max_score,
    ROUND(
        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM strength_scores)), 2
    ) as distribution_percentage
FROM strength_scores s
JOIN gallup_strengths g ON s.strength_name = g.strength_name
WHERE s.ttl_expires_at > CURRENT_TIMESTAMP
GROUP BY s.strength_name, s.theme
ORDER BY assessment_count DESC;

-- =============================================================================
-- PERFORMANCE INDEXES
-- =============================================================================

-- Additional composite indexes for complex queries
CREATE INDEX idx_session_status ON assessment_sessions(status);
CREATE INDEX idx_session_status_expires ON assessment_sessions(status, expires_at);
CREATE INDEX idx_response_session ON assessment_responses(session_id);
CREATE INDEX idx_response_session_question ON assessment_responses(session_id, question_id);
CREATE INDEX idx_score_session_rank ON strength_scores(session_id, rank_position);
CREATE INDEX idx_audit_session_action_time ON audit_trails(session_id, action_type, timestamp);
CREATE INDEX idx_consent_session_timestamp ON consent_records(session_id, consent_timestamp);

-- TTL cleanup indexes (without problematic WHERE clauses)
CREATE INDEX idx_expired_sessions ON assessment_sessions(expires_at);
CREATE INDEX idx_expired_responses ON assessment_responses(ttl_expires_at);
CREATE INDEX idx_expired_scores ON strength_scores(ttl_expires_at);
CREATE INDEX idx_expired_consent ON consent_records(ttl_expires_at);

-- =============================================================================
-- SECURITY AND COMPLIANCE NOTES
-- =============================================================================
-- 1. All sensitive data (IP addresses, user agents) are stored as hashes
-- 2. TTL is enforced at application level with database cleanup jobs
-- 3. Foreign key constraints ensure referential integrity
-- 4. Audit trails capture all data modifications
-- 5. Consent withdrawal is supported through timestamp updates
-- 6. Data export capabilities built into structure
-- 7. Session isolation prevents cross-contamination
-- 8. Performance optimized for psychological assessment workflows
-- =============================================================================