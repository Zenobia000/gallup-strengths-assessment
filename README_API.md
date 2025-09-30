# Gallup Strengths Assessment API

A comprehensive FastAPI-based psychological assessment system with GDPR compliance and modern security features.

## Features

- 🔐 **Security First**: JWT authentication, bcrypt password hashing, audit logging
- 📊 **Psychology Compliant**: 24-hour TTL, consent management, GDPR compliance
- 🚀 **Modern Stack**: FastAPI, SQLAlchemy 2.0, Pydantic v2, async/await
- 📱 **API Ready**: RESTful design, OpenAPI docs, CORS support
- 🔒 **Privacy Protection**: IP anonymization, data retention policies, consent tracking

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (especially SECRET_KEY)
nano .env
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Run the Application

```bash
# Development mode
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2023-12-07T10:00:00Z",
  "version": "1.0.0",
  "database": "connected",
  "features": {
    "audit_logging": true,
    "consent_required": true,
    "data_anonymization": true
  }
}
```

## API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

## Project Structure

```
app/
├── core/
│   ├── config.py          # Configuration management
│   ├── database.py        # Database connections
│   ├── security.py        # Security utilities
│   └── exceptions.py      # Custom exceptions
├── api/
│   └── v1/
│       ├── consent.py     # Consent management
│       ├── sessions.py    # Session lifecycle
│       └── assessments.py # Assessment endpoints
├── models/
│   ├── consent.py         # Consent Pydantic models
│   ├── session.py         # Session models
│   ├── assessment.py      # Assessment models
│   └── strength.py        # Strength models
├── services/
│   ├── consent_service.py # Consent business logic
│   └── session_service.py # Session management
├── middleware/
│   ├── cors.py           # CORS configuration
│   └── logging.py        # Request logging
└── main.py               # FastAPI application
```

## Core Components

### Configuration Management
- Environment-based settings with Pydantic
- Psychology-specific compliance settings
- Security configuration with validation

### Database Layer
- SQLAlchemy 2.0 with async support
- SQLite with WAL mode for concurrency
- Connection pooling and health checks

### Security Features
- JWT token management with rotation
- Bcrypt password hashing
- Audit logging for all operations
- IP address anonymization
- CSRF protection utilities

### Compliance Features
- 24-hour session TTL for psychological data
- Comprehensive consent management
- GDPR-compliant data retention
- Audit trails for all operations

## Environment Variables

Key environment variables to configure:

```bash
# Security (REQUIRED)
SECRET_KEY="your-secure-secret-key-minimum-32-characters"

# Database
DATABASE_URL="sqlite+aiosqlite:///./gallup_strengths.db"

# Compliance
SESSION_TTL_HOURS=24
CONSENT_REQUIRED=true
AUDIT_LOGGING_ENABLED=true

# CORS for frontend
BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8080"
```

## API Endpoints

### System Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /health/detailed` - Detailed system status

### Session Management
- `POST /api/v1/sessions/create` - Create assessment session
- `GET /api/v1/sessions/{session_id}/status` - Get session status
- `POST /api/v1/sessions/{session_id}/validate` - Validate session
- `DELETE /api/v1/sessions/{session_id}` - Terminate session

### Consent Management
- `POST /api/v1/consent/give` - Record consent
- `GET /api/v1/consent/status/{session_id}` - Check consent status
- `POST /api/v1/consent/withdraw` - Withdraw consent
- `GET /api/v1/consent/required` - Get required consent types

### Assessment
- `POST /api/v1/assessments/{session_id}/start` - Start assessment
- `GET /api/v1/assessments/{session_id}/current-question` - Get current question
- `POST /api/v1/assessments/{session_id}/answer` - Submit answer
- `GET /api/v1/assessments/{session_id}/progress` - Get progress
- `GET /api/v1/assessments/{session_id}/result` - Get results

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Quality
```bash
# Format code
black app/

# Type checking
mypy app/

# Linting
ruff check app/
```

### Database Management
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

## Security Considerations

1. **Change SECRET_KEY**: Generate a secure 32+ character secret key
2. **HTTPS Only**: Use HTTPS in production
3. **Database Security**: Secure database file permissions
4. **CORS Configuration**: Restrict origins in production
5. **Rate Limiting**: Implement rate limiting for production use
6. **Monitoring**: Monitor audit logs for suspicious activity

## Compliance Features

### GDPR Compliance
- Explicit consent management
- Right to withdraw consent
- Data retention policies
- Audit trails for all data operations
- IP address anonymization

### Psychological Assessment Ethics
- 24-hour data TTL
- Session isolation
- Response time tracking for validity
- Comprehensive audit logging

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database file permissions
   ls -la gallup_strengths.db

   # Verify WAL mode
   sqlite3 gallup_strengths.db "PRAGMA journal_mode;"
   ```

2. **JWT Token Issues**
   ```bash
   # Verify SECRET_KEY length
   python -c "import os; print(len(os.getenv('SECRET_KEY', '')))"
   ```

3. **CORS Errors**
   ```bash
   # Check CORS origins configuration
   echo $BACKEND_CORS_ORIGINS
   ```

### Health Check Failures
- Verify database connectivity
- Check file permissions
- Confirm environment variables are loaded

## Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup
- Set `DEBUG=false`
- Use strong `SECRET_KEY`
- Configure proper CORS origins
- Set up SSL/TLS certificates
- Configure reverse proxy (nginx)

## Support

For questions or issues:
1. Check the API documentation at `/docs`
2. Review audit logs for errors
3. Verify environment configuration
4. Check database connectivity

## License

This project follows psychological assessment ethics and GDPR compliance requirements.