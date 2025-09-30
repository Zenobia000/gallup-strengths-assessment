# Gallup Strengths Assessment System - Maintenance Manual

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Installation and Setup](#installation-and-setup)
3. [Configuration Management](#configuration-management)
4. [Database Administration](#database-administration)
5. [Cache Management](#cache-management)
6. [Performance Monitoring](#performance-monitoring)
7. [Backup and Recovery](#backup-and-recovery)
8. [Security Considerations](#security-considerations)
9. [API Documentation Summary](#api-documentation-summary)
10. [Troubleshooting](#troubleshooting)
11. [Maintenance Procedures](#maintenance-procedures)

---

## System Architecture Overview

### Technology Stack
- **Backend Framework**: FastAPI (Python 3.9+)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Caching**: Redis
- **Frontend**: HTML5/CSS3/JavaScript (Vanilla)
- **PDF Generation**: ReportLab
- **Testing**: Pytest
- **ASGI Server**: Uvicorn

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Database      │
│   (HTML/CSS/JS) │◄──►│   Backend       │◄──►│   SQLite/       │
│                 │    │                 │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Redis Cache   │
                       │                 │
                       └─────────────────┘
```

### Directory Structure
```
strength-system/
├── src/main/python/
│   ├── api/
│   │   ├── main.py                 # FastAPI application entry point
│   │   └── routes/                 # API route modules
│   ├── core/
│   │   ├── assessment.py           # Assessment logic
│   │   ├── config.py              # Configuration settings
│   │   ├── database.py            # Database connection
│   │   └── scoring/               # Scoring engine
│   ├── models/
│   │   └── models.py              # SQLAlchemy models
│   └── services/
│       ├── cache_service.py       # Cache management
│       └── report_service.py      # Report generation
├── src/main/resources/
│   └── static/                    # Frontend assets
├── src/test/                      # Test suites
├── docs/                         # Documentation
└── requirements.txt              # Python dependencies
```

---

## Installation and Setup

### Prerequisites
- Python 3.9 or higher
- Redis server
- PostgreSQL (for production)
- Git

### Development Environment Setup

1. **Clone the Repository**
```bash
git clone [repository-url]
cd strength-system
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env file with your configuration
```

5. **Initialize Database**
```bash
python -c "from src.main.python.core.database import init_db; init_db()"
```

6. **Start Redis Server**
```bash
redis-server
```

7. **Run Development Server**
```bash
cd src/main/python
uvicorn api.main:app --reload --host 0.0.0.0 --port 8004
```

### Production Deployment

1. **Environment Setup**
```bash
# Set production environment variables
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:password@localhost/strengths_db
export REDIS_URL=redis://localhost:6379
export SECRET_KEY=your-secret-key
```

2. **Database Migration (PostgreSQL)**
```bash
# Create database
createdb strengths_db

# Run migrations
python -c "from src.main.python.core.database import init_db; init_db()"
```

3. **Start Production Server**
```bash
cd src/main/python
uvicorn api.main:app --host 0.0.0.0 --port 8004 --workers 4
```

### Docker Deployment

1. **Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
EXPOSE 8004

CMD ["uvicorn", "src.main.python.api.main:app", "--host", "0.0.0.0", "--port", "8004"]
```

2. **Docker Compose Setup**
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8004:8004"
    depends_on:
      - redis
      - postgres
    environment:
      - DATABASE_URL=postgresql://user:password@postgres/strengths_db
      - REDIS_URL=redis://redis:6379

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: strengths_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Configuration Management

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Deployment environment | development | No |
| `DATABASE_URL` | Database connection string | sqlite:///./test.db | No |
| `REDIS_URL` | Redis connection string | redis://localhost:6379 | No |
| `SECRET_KEY` | Application secret key | dev-secret | Yes (prod) |
| `CACHE_EXPIRE_TIME` | Cache expiration (seconds) | 3600 | No |
| `MAX_ASSESSMENT_TIME` | Max assessment duration | 1800 | No |

### Configuration Files

**src/main/python/core/config.py**
```python
class Settings:
    app_name: str = "Gallup Strengths Assessment"
    environment: str = "development"
    database_url: str = "sqlite:///./test.db"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "dev-secret-key"

    # Assessment settings
    max_assessment_time: int = 1800  # 30 minutes
    cache_expire_time: int = 3600    # 1 hour

    # PDF settings
    pdf_font_size: int = 12
    pdf_margin: int = 50
```

---

## Database Administration

### Database Schema

**Users Table**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Assessments Table**
```sql
CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    responses TEXT,  -- JSON format
    big_five_scores TEXT,  -- JSON format
    gallup_strengths TEXT,  -- JSON format
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255) UNIQUE
);
```

### Database Operations

#### Backup Operations
```bash
# SQLite backup
cp strengths.db strengths_backup_$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump strengths_db > backup_$(date +%Y%m%d).sql
```

#### Database Maintenance
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('strengths_db'));

-- Analyze table statistics
ANALYZE users;
ANALYZE assessments;

-- Vacuum to reclaim space
VACUUM ANALYZE;
```

---

## Cache Management

### Redis Configuration

**Connection Settings**
```python
# src/main/python/services/cache_service.py
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True
)
```

### Cache Strategies

#### Assessment Progress Caching
```python
# Cache assessment progress
def cache_assessment_progress(session_id: str, responses: dict):
    key = f"assessment:progress:{session_id}"
    redis_client.setex(key, 1800, json.dumps(responses))  # 30 min TTL

# Retrieve cached progress
def get_cached_progress(session_id: str):
    key = f"assessment:progress:{session_id}"
    cached_data = redis_client.get(key)
    return json.loads(cached_data) if cached_data else None
```

### Cache Administration

#### Cache Monitoring Commands
```bash
# Connect to Redis CLI
redis-cli

# Check memory usage
INFO memory

# View all keys
KEYS *

# Check specific key
GET assessment:progress:session123

# View key TTL
TTL assessment:progress:session123

# Clear specific pattern
EVAL "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 assessment:*
```

---

## Performance Monitoring

### Application Metrics

#### Key Performance Indicators
- **Response Time**: API endpoint response times
- **Throughput**: Requests per second
- **Error Rate**: Failed requests percentage
- **Database Performance**: Query execution times
- **Cache Hit Ratio**: Cache effectiveness
- **Memory Usage**: Application memory consumption

#### Health Check Endpoints
```python
@app.get("/health")
async def health_check():
    """System health check endpoint"""
    checks = {
        "database": await check_database_health(),
        "redis": await check_redis_health(),
        "disk_space": check_disk_space(),
        "memory_usage": check_memory_usage()
    }

    overall_status = "healthy" if all(checks.values()) else "unhealthy"

    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow()
    }
```

---

## Backup and Recovery

### Backup Strategy

#### Automated Backup Script
```bash
#!/bin/bash
# backup_script.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="strengths_db"

# Create backup directory
mkdir -p $BACKUP_DIR/database
mkdir -p $BACKUP_DIR/redis
mkdir -p $BACKUP_DIR/files

# Database backup
pg_dump $DB_NAME | gzip > $BACKUP_DIR/database/db_backup_$DATE.sql.gz

# Redis backup
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis/redis_backup_$DATE.rdb

# Application files backup
tar -czf $BACKUP_DIR/files/app_backup_$DATE.tar.gz /path/to/app

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Disaster Recovery Procedures

#### Database Recovery
```bash
# PostgreSQL point-in-time recovery
pg_restore -d strengths_db backup_20241201_120000.sql.gz

# Verify data integrity
psql strengths_db -c "SELECT COUNT(*) FROM users;"
psql strengths_db -c "SELECT COUNT(*) FROM assessments;"
```

---

## Security Considerations

### Authentication and Authorization

#### Session Management
```python
# src/main/python/core/security.py
from cryptography.fernet import Fernet

class SessionManager:
    def __init__(self, secret_key: str):
        self.cipher = Fernet(secret_key.encode())

    def create_session(self, user_data: dict) -> str:
        session_data = json.dumps(user_data)
        encrypted_session = self.cipher.encrypt(session_data.encode())
        return encrypted_session.decode()

    def validate_session(self, session_token: str) -> dict:
        try:
            decrypted_data = self.cipher.decrypt(session_token.encode())
            return json.loads(decrypted_data.decode())
        except Exception:
            return None
```

### Data Protection

#### Data Encryption
- **In Transit**: TLS/SSL encryption for all API communications
- **At Rest**: Database encryption for sensitive data
- **Cache**: Redis AUTH and encryption for cached data

### Security Headers
```python
# src/main/python/api/main.py
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

---

## API Documentation Summary

### Core Endpoints

#### Assessment API
```
GET    /api/v1/health                    # System health check
POST   /api/v1/sessions                  # Create new session
GET    /api/v1/scoring/questions         # Get assessment questions
POST   /api/v1/scoring/submit            # Submit assessment responses
GET    /api/v1/sessions/{id}/results     # Retrieve assessment results
POST   /api/v1/reports/generate/session  # Generate PDF report
```

#### Cache Management API
```
GET    /api/v1/cache/stats              # Cache statistics
GET    /api/v1/cache/health             # Cache health check
POST   /api/v1/cache/warm               # Warm cache with common data
DELETE /api/v1/cache/clear              # Clear cache data
```

### Request/Response Examples

#### Start Assessment
```http
POST /api/v1/sessions
Content-Type: application/json

{
    "user_name": "John Doe",
    "user_email": "john@example.com"
}

Response:
{
    "session_id": "abc123def456",
    "status": "created",
    "expires_at": "2024-12-01T15:30:00Z"
}
```

#### Submit Assessment
```http
POST /api/v1/scoring/submit
Content-Type: application/json

{
    "session_id": "abc123def456",
    "responses": [
        {"question_id": 1, "score": 4},
        {"question_id": 2, "score": 3}
    ]
}

Response:
{
    "success": true,
    "message": "Assessment submitted successfully",
    "session_id": "abc123def456"
}
```

---

## Troubleshooting

### Common Issues and Solutions

#### Application Won't Start

**Symptom**: Server fails to start with import errors
**Diagnosis**:
```bash
cd src/main/python
python -c "import api.main"
```
**Solutions**:
1. Check Python version compatibility
2. Verify all dependencies are installed
3. Check for conflicting package versions
4. Ensure PYTHONPATH is set correctly

**Symptom**: Database connection errors
**Diagnosis**:
```bash
python -c "from core.database import engine; print(engine.url)"
```
**Solutions**:
1. Verify database server is running
2. Check connection string format
3. Ensure database exists
4. Verify credentials and permissions

#### Performance Issues

**Symptom**: Slow API responses
**Diagnosis**:
```bash
# Check database query performance
EXPLAIN ANALYZE SELECT * FROM assessments WHERE user_id = 1;

# Monitor Redis performance
redis-cli --latency-history
```
**Solutions**:
1. Add database indexes
2. Optimize slow queries
3. Implement caching strategy
4. Scale Redis instance

### Log Analysis Commands
```bash
# Find recent errors
grep -i error /var/log/strengths-app.log | tail -20

# Monitor API response times
grep "Duration:" /var/log/strengths-app.log | awk '{print $NF}' | sort -n | tail -10

# Check for database connection issues
grep -i "database" /var/log/strengths-app.log | grep -i error
```

---

## Maintenance Procedures

### Daily Maintenance Tasks

#### System Health Check
```bash
#!/bin/bash
# daily_health_check.sh

echo "=== Daily Health Check - $(date) ==="

# Check application status
curl -s http://localhost:8004/api/v1/health | jq .

# Check database status
psql strengths_db -c "SELECT COUNT(*) FROM users;"

# Check Redis status
redis-cli ping

# Check disk space
df -h | grep -E "(/$|/var|/tmp)"

# Check memory usage
free -h

# Check recent errors
tail -50 /var/log/strengths-app.log | grep -i error
```

### Weekly Maintenance Tasks

#### Database Optimization
```sql
-- Analyze table statistics
ANALYZE users;
ANALYZE assessments;

-- Vacuum to reclaim space
VACUUM ANALYZE;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

#### Cache Optimization
```bash
# Redis maintenance
redis-cli BGREWRITEAOF  # Rewrite AOF file
redis-cli MEMORY PURGE  # Free unused memory
redis-cli INFO memory   # Check memory usage
```

### Monthly Maintenance Tasks

#### Security Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Python packages
pip install --upgrade -r requirements.txt

# Review security logs
grep -i "authentication\|authorization\|failed\|denied" /var/log/strengths-app.log
```

---

## Contact Information

For technical support and maintenance issues:

- **System Administrator**: [admin@domain.com]
- **Development Team**: [dev-team@domain.com]
- **Emergency Contact**: [emergency@domain.com]

### Escalation Procedures

1. **Level 1**: Application issues, general maintenance
2. **Level 2**: Database problems, performance issues
3. **Level 3**: Security incidents, data corruption
4. **Level 4**: Complete system failure, disaster recovery

---

*Last Updated: December 2024*
*Version: 1.0*
*Document Maintainer: System Administrator*