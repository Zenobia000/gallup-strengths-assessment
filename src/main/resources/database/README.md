# Gallup Strengths Assessment Database Documentation

## Overview

This database system provides comprehensive support for psychological assessments with full compliance features including:

- **24-hour TTL**: Automatic data expiration for sensitive assessment data
- **GDPR Compliance**: Data retention policies, consent tracking, audit trails
- **Data Anonymization**: IP address hashing, personal data protection
- **Audit Logging**: Complete operation tracking for regulatory compliance
- **Session Isolation**: Each assessment session completely isolated
- **Data Integrity**: Foreign key constraints, data validation

## Database Architecture

### Core Design Principles

1. **Psychology-First Design**: Built specifically for psychological assessment workflows
2. **Compliance by Design**: GDPR and privacy compliance built into the database structure
3. **Performance Optimized**: Indexed for assessment-specific query patterns
4. **Data Safety**: Multiple layers of data protection and validation
5. **Scalability**: Designed to handle thousands of concurrent assessments

### Technology Stack

- **Database**: SQLite with WAL mode for concurrency
- **ORM**: SQLAlchemy 2.0 with async/await support
- **Language**: Python 3.8+
- **Compliance**: GDPR-ready with audit trails

## Database Schema

### Core Tables

#### assessment_sessions
**Purpose**: Central session management with TTL
- `session_id` (PRIMARY KEY): Unique session identifier
- `status`: Session state (created, active, completed, expired, abandoned)
- `participant_type`: Type of participant (individual, team_member, leader, student)
- `expires_at`: 24-hour TTL timestamp
- `metadata`: JSON for flexible session data

#### consent_records
**Purpose**: GDPR compliance and consent tracking
- `consent_id` (PRIMARY KEY): Unique consent record
- `session_id` (FOREIGN KEY): Links to assessment session
- `consent_types`: JSON array of consent types given
- `consent_timestamp`: When consent was provided
- `ttl_expires_at`: 24-hour expiration

#### assessment_responses
**Purpose**: Individual question responses with performance tracking
- `response_id` (PRIMARY KEY): Unique response identifier
- `session_id` (FOREIGN KEY): Links to session
- `question_id` (FOREIGN KEY): Links to question
- `selected_value`: Participant's response
- `response_time_ms`: Time taken to answer
- `confidence_level`: Participant's confidence (1-5 scale)

#### strength_scores
**Purpose**: Calculated assessment results
- `score_id` (PRIMARY KEY): Unique score identifier
- `session_id` (FOREIGN KEY): Links to session
- `strength_name`: Name of the strength (links to Gallup strengths)
- `score`: Calculated strength score
- `rank_position`: 1-34 ranking position
- `confidence_interval_lower/upper`: Statistical confidence bounds

### Reference Data Tables

#### gallup_strengths
**Purpose**: 34 Gallup strength themes with comprehensive metadata
- All 34 official Gallup strength themes
- Detailed descriptions and characteristics
- Development suggestions and blind spots
- Leadership applications and team contributions

#### questions
**Purpose**: Mini-IPIP question bank for personality assessment
- 50 validated questions covering Big Five personality factors
- Likert scale responses (1-5)
- Theme mappings to Gallup strengths
- Scoring keys for assessment calculation

### Compliance Tables

#### audit_trails
**Purpose**: Complete operation tracking for regulatory compliance
- Captures all data modifications
- Anonymized IP and user agent tracking
- JSON-based old/new value tracking
- Success/failure logging

#### privacy_requests
**Purpose**: GDPR subject access request management
- Data export requests
- Data deletion requests
- Request processing workflow
- Compliance documentation

## Data Flow

### Assessment Lifecycle

1. **Session Creation**: New session created with 24-hour TTL
2. **Consent Collection**: Required consent types recorded with audit
3. **Assessment Delivery**: Questions served based on configuration
4. **Response Collection**: Answers stored with timing and confidence data
5. **Score Calculation**: Strength scores computed using validated algorithms
6. **Results Delivery**: Personalized strength reports generated
7. **Data Expiration**: All data automatically expires after 24 hours

### Compliance Workflow

1. **Audit Logging**: All operations automatically logged
2. **Data Anonymization**: Personal identifiers hashed immediately
3. **TTL Enforcement**: Scheduled cleanup of expired data
4. **Privacy Requests**: GDPR request handling workflow
5. **Data Export**: Compliance-ready data export capabilities

## Performance Optimization

### Indexing Strategy

- **Primary Keys**: All tables have optimized primary keys
- **Foreign Keys**: All relationships properly indexed
- **Query Patterns**: Indexes aligned with application queries
- **TTL Queries**: Special indexes for cleanup operations

### Key Indexes

```sql
-- Session management
CREATE INDEX idx_session_status_expires ON assessment_sessions(status, expires_at);
CREATE INDEX idx_session_created ON assessment_sessions(created_at);

-- Response tracking
CREATE INDEX idx_response_session_question ON assessment_responses(session_id, question_id);
CREATE INDEX idx_response_expires ON assessment_responses(ttl_expires_at);

-- Audit queries
CREATE INDEX idx_audit_session_action_time ON audit_trails(session_id, action_type, timestamp);

-- TTL cleanup
CREATE INDEX idx_expired_sessions ON assessment_sessions(expires_at) WHERE expires_at < CURRENT_TIMESTAMP;
```

## Security Features

### Data Protection

1. **IP Address Hashing**: All IP addresses stored as SHA-256 hashes
2. **User Agent Hashing**: User agents anonymized for privacy
3. **Session Isolation**: Complete data isolation between sessions
4. **Foreign Key Constraints**: Data integrity enforced at database level
5. **Input Validation**: All inputs validated before storage

### Compliance Features

1. **Audit Trails**: Complete modification history
2. **Consent Management**: Granular consent tracking
3. **Data Retention**: Automated TTL enforcement
4. **Privacy Requests**: Built-in GDPR request handling
5. **Data Export**: Compliance-ready export formats

## Usage Examples

### Database Initialization

```bash
# Initialize complete database
python scripts/init_database.py init

# Create schema only
python scripts/init_database.py schema

# Load seed data only
python scripts/init_database.py seed --force

# Health check
python scripts/init_database.py health

# TTL cleanup
python scripts/init_database.py cleanup

# Reset database
python scripts/init_database.py reset --backup
```

### Application Integration

```python
from app.core.database import get_async_db

async def create_assessment_session(participant_type: str):
    async with get_async_db() as db:
        session = await db.execute("""
            INSERT INTO assessment_sessions (
                session_id, status, participant_type,
                expires_at
            ) VALUES (?, ?, ?, datetime('now', '+24 hours'))
        """, (session_id, 'created', participant_type))
        await db.commit()
        return session_id
```

## Monitoring and Maintenance

### Health Monitoring

The system provides comprehensive health monitoring:

```bash
# Check overall database health
python scripts/init_database.py health

# Validate data integrity
python scripts/init_database.py validate

# Test async operations
python scripts/init_database.py test
```

### Maintenance Tasks

1. **TTL Cleanup**: Run daily to remove expired data
2. **Health Checks**: Monitor database status
3. **Backup Creation**: Regular database backups
4. **Index Optimization**: Periodic index maintenance
5. **Audit Log Archival**: Archive old audit records

### Performance Monitoring

Key metrics to monitor:

- Session completion rates
- Average response times
- Database query performance
- TTL cleanup efficiency
- Audit trail growth

## Troubleshooting

### Common Issues

1. **Schema Missing**: Run `python scripts/init_database.py schema`
2. **Seed Data Missing**: Run `python scripts/init_database.py seed --force`
3. **Performance Issues**: Check indexes with health command
4. **TTL Cleanup Failures**: Check disk space and permissions
5. **Foreign Key Violations**: Run validation to identify orphaned records

### Diagnostic Commands

```bash
# Comprehensive health check
python scripts/init_database.py health --verbose

# Integrity validation
python scripts/init_database.py validate

# Cleanup preview
python scripts/init_database.py cleanup --dry-run

# Test all operations
python scripts/init_database.py test --verbose
```

## Development Guidelines

### Schema Changes

1. Always update both `schema.sql` and models
2. Create migration scripts for existing data
3. Test schema changes on backup database
4. Update seed data if structure changes
5. Document breaking changes

### Performance Guidelines

1. Use appropriate indexes for query patterns
2. Minimize JSON queries in hot paths
3. Implement proper TTL cleanup scheduling
4. Monitor query performance regularly
5. Use connection pooling appropriately

### Compliance Guidelines

1. All personal data must be anonymized
2. Implement audit logging for all modifications
3. Respect TTL expiration strictly
4. Handle privacy requests promptly
5. Document all compliance procedures

## Migration and Deployment

### Production Deployment

1. Create database backup
2. Run schema validation
3. Initialize with production settings
4. Load seed data
5. Verify health status
6. Configure TTL cleanup cron job

### Backup Strategy

- Daily automated backups
- Pre-deployment backups
- Weekly backup verification
- Offsite backup storage
- Retention policy compliance

## Support and Resources

### Documentation
- [Gallup Strengths Documentation](https://www.gallup.com/cliftonstrengths/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [GDPR Compliance Guide](https://gdpr.eu/)

### Files
- `/src/main/resources/database/schema.sql` - Complete database schema
- `/src/main/resources/database/seed_data.sql` - Reference data and test data
- `/scripts/init_database.py` - Database management script
- `/app/core/database.py` - Database connection management

### Monitoring
- Database health checks
- Performance metrics
- Compliance audits
- Error logging and alerting