# 🚀 Deployment Guide - Gallup Strengths Assessment v4.0

**Last Updated**: 2025-10-03
**Status**: Production Ready (95/100)
**Philosophy**: Linus Torvalds Pragmatism - "Make it work, make it right, make it fast"

---

## 📋 Prerequisites

### Required
- **Python**: 3.11+ (tested on 3.11)
- **pip**: Latest version
- **Git**: For version control
- **Domain**: (Optional) For production HTTPS

### Optional
- **Docker**: 20.10+ (recommended for production)
- **PostgreSQL**: 15+ (for >50 concurrent users)
- **Nginx/Traefik**: Reverse proxy for HTTPS

---

## 🎯 Quick Start (< 5 minutes)

### Local Development
```bash
# 1. Clone repository
git clone https://github.com/Zenobia000/gallup-strengths-assessment.git
cd gallup-strengths-assessment

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env from template
cp .env.example .env
# Edit .env and set your SECRET_KEY (already generated in template)

# 5. Initialize database
python -c "from database.engine import init_database; init_database()"

# 6. Start development server
cd src/main/python
uvicorn api.main:app --host 0.0.0.0 --port 8005 --reload

# 7. Access the application
# Frontend: http://localhost:8005/landing.html
# API Docs: http://localhost:8005/api/docs
# Health Check: http://localhost:8005/api/system/health
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8005 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
FastAPI application started successfully
V4 File storage version ready
API documentation: http://localhost:8005/api/docs
File storage initialized
INFO:     Application startup complete.
```

---

## 🔐 Environment Configuration

### Creating .env File

**Step 1: Copy template**
```bash
cp .env.example .env
```

**Step 2: Configure critical variables**

```bash
# Database (SQLite for development)
DATABASE_URL=sqlite:///D:/path/to/your/project/data/gallup_strengths.db

# CORS Origins (add your frontend domain)
CORS_ORIGINS=http://localhost:3000,http://localhost:8005

# Secret Key (already generated, KEEP THIS SECRET!)
SECRET_KEY=bT_L57WIBRrNGyWj2ucHV_Vd7tDW6fZqfPNXfDIHfnw

# Server Configuration
HOST=0.0.0.0
PORT=8005
WORKERS=4

# Storage
STORAGE_BACKEND=local
REPORT_RETENTION_DAYS=7

# Logging
LOG_LEVEL=INFO
```

**Step 3: Verify configuration**
```bash
python -c "from core.config import get_settings; s = get_settings(); print(f'DB: {s.database_url}'); print(f'CORS: {s.allowed_origins}')"
```

**Expected output:**
```
DB: sqlite:///D:/path/to/your/project/data/gallup_strengths.db
CORS: ['http://localhost:3000', 'http://localhost:8005']
```

---

## 🐳 Method 1: Docker Deployment (Recommended)

### Why Docker?
- ✅ Consistent environment across dev/staging/production
- ✅ Easy rollback (`docker-compose down && docker-compose up`)
- ✅ Isolated dependencies
- ✅ Simple scaling (docker-compose scale)

### Build and Run

```bash
# 1. Ensure .env file exists
cp .env.example .env
# Edit .env with production values

# 2. Build Docker image
docker-compose build

# 3. Start services
docker-compose up -d

# 4. Check health
curl http://localhost:8000/api/system/health

# 5. View logs
docker-compose logs -f app

# 6. Stop services
docker-compose down
```

### Docker Configuration

**Dockerfile highlights:**
- Base image: `python:3.11-slim`
- Health check: Built-in `/api/system/health`
- Volumes: `/app/data`, `/app/output`, `/app/logs`
- Port: 8000 (configurable via .env)

**docker-compose.yml highlights:**
- Auto-restart: `unless-stopped`
- Environment: Loaded from `.env`
- Volumes: Persistent data storage
- Health checks: 30s interval

### Production Docker Commands

```bash
# Build with specific tag
docker build -t gallup-assessment:v4.0 .

# Run with custom configuration
docker run -d \
  --name gallup-app \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  --env-file .env \
  gallup-assessment:v4.0

# View logs
docker logs -f gallup-app

# Execute commands inside container
docker exec -it gallup-app python -m pytest src/test/

# Stop and remove
docker stop gallup-app && docker rm gallup-app
```

---

## ☁️ Method 2: Platform as a Service (Render/Railway)

### Why PaaS?
- ✅ Zero infrastructure management
- ✅ Auto-scaling
- ✅ Built-in HTTPS
- ✅ Free tier for testing

### Render Deployment

**Step 1: Prepare repository**
```bash
# Ensure all deployment files are committed
git add .env.example Dockerfile requirements.txt gunicorn_conf.py
git commit -m "chore: add deployment configuration"
git push origin main
```

**Step 2: Create Render Web Service**
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `gallup-strengths-assessment`
   - **Region**: Choose closest to users
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn src.main.python.api.main:app -c gunicorn_conf.py`

**Step 3: Set Environment Variables**
Add in Render dashboard:
```
DATABASE_URL=sqlite:///./data/gallup_strengths.db
CORS_ORIGINS=https://your-app.onrender.com
SECRET_KEY=<your-generated-secret-key>
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=INFO
```

**Step 4: Deploy**
- Click "Create Web Service"
- Wait ~5 minutes for build
- Access at `https://your-app.onrender.com`

**Health check:**
```bash
curl https://your-app.onrender.com/api/system/health
```

### Railway Deployment

**Similar process:**
1. [railway.app](https://railway.app) → New Project
2. Connect GitHub repo
3. Railway auto-detects Dockerfile
4. Set environment variables in dashboard
5. Deploy automatically on git push

**Cost comparison:**
- **Render**: Free tier (750 hrs/month), then $7/month
- **Railway**: $5/month hobby plan, $20/month pro

---

## 🖥️ Method 3: Manual Linux Deployment

### Ubuntu/Debian Server Setup

**Step 1: System preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install system dependencies
sudo apt install git nginx sqlite3 -y
```

**Step 2: Application setup**
```bash
# Create application directory
sudo mkdir -p /opt/gallup-strengths
cd /opt/gallup-strengths

# Clone repository
sudo git clone https://github.com/Zenobia000/gallup-strengths-assessment.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
sudo nano .env
# Paste your production configuration
```

**Step 3: Create systemd service**
```bash
sudo nano /etc/systemd/system/gallup-assessment.service
```

**Service file content:**
```ini
[Unit]
Description=Gallup Strengths Assessment API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/gallup-strengths
Environment="PATH=/opt/gallup-strengths/venv/bin"
ExecStart=/opt/gallup-strengths/venv/bin/gunicorn src.main.python.api.main:app -c gunicorn_conf.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Step 4: Start service**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable gallup-assessment

# Start service
sudo systemctl start gallup-assessment

# Check status
sudo systemctl status gallup-assessment

# View logs
sudo journalctl -u gallup-assessment -f
```

**Step 5: Configure Nginx reverse proxy**
```bash
sudo nano /etc/nginx/sites-available/gallup-assessment
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for PDF generation
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if needed)
    location /static {
        alias /opt/gallup-strengths/src/main/resources/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/gallup-assessment /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Step 6: Setup HTTPS with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 🗄️ Database Migration (SQLite → PostgreSQL)

### When to Migrate?
- ✅ You have >20 concurrent users
- ✅ You're experiencing database lock errors
- ✅ You need replication/backup
- ✅ You're preparing for production scale

### Migration Steps

**Step 1: Install PostgreSQL**
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Step 2: Create database and user**
```bash
sudo -u postgres psql

CREATE DATABASE gallup_strengths;
CREATE USER gallup_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE gallup_strengths TO gallup_user;
\q
```

**Step 3: Update .env**
```bash
# Change from SQLite
# DATABASE_URL=sqlite:///./data/gallup_strengths.db

# To PostgreSQL
DATABASE_URL=postgresql://gallup_user:your-secure-password@localhost:5432/gallup_strengths
```

**Step 4: Install PostgreSQL driver**
```bash
pip install psycopg2-binary
```

**Step 5: Run migration**
```bash
# Initialize PostgreSQL schema
python -c "from database.engine import init_database; init_database(force_recreate=True)"

# Verify tables created
psql -U gallup_user -d gallup_strengths -c "\dt"
```

**Step 6: Migrate data (if needed)**
```bash
# Export from SQLite
sqlite3 data/gallup_strengths.db .dump > sqlite_dump.sql

# Import to PostgreSQL (requires manual schema mapping)
# Use scripts/database/migrate_to_v4_sqlalchemy.py as reference
```

**Step 7: Test**
```bash
# Start application
uvicorn src.main.python.api.main:app --reload

# Health check
curl http://localhost:8005/api/system/health
# Should show "database_status": "connected"
```

---

## 🔍 Monitoring & Maintenance

### Health Checks

**Endpoint**: `GET /api/system/health`

**Healthy response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-03T10:00:00",
  "version": "1.0.0",
  "database_status": "connected",
  "services": {
    "assessment": "ready",
    "scoring": "ready",
    "reporting": "ready",
    "v4_engine": "ready"
  }
}
```

**Monitor this endpoint:**
- **Uptime monitoring**: Every 1 minute
- **Alert threshold**: 3 consecutive failures
- **Tools**: UptimeRobot (free), Pingdom, StatusCake

### Application Logs

**Location:**
- **Docker**: `docker logs -f gallup-app`
- **Systemd**: `journalctl -u gallup-assessment -f`
- **Local**: `logs/gunicorn-access.log`, `logs/gunicorn-error.log`

**Key logs to monitor:**
- `ERROR` level logs (should be <1% of requests)
- `Database session error` (indicates connection issues)
- `429 Too Many Requests` (rate limiting triggered)

### Database Backups

#### SQLite Backup (Automatic)
```bash
# Create backup script
sudo nano /usr/local/bin/backup-gallup-db.sh
```

**Script content:**
```bash
#!/bin/bash
BACKUP_DIR=/backups/gallup-db
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
sqlite3 /opt/gallup-strengths/data/gallup_strengths.db ".backup $BACKUP_DIR/db-$TIMESTAMP.db"
# Keep only last 30 days
find $BACKUP_DIR -name "db-*.db" -mtime +30 -delete
echo "Backup completed: db-$TIMESTAMP.db"
```

**Make executable and schedule:**
```bash
sudo chmod +x /usr/local/bin/backup-gallup-db.sh

# Add to crontab (every 6 hours)
sudo crontab -e
0 */6 * * * /usr/local/bin/backup-gallup-db.sh >> /var/log/gallup-backup.log 2>&1
```

#### PostgreSQL Backup
```bash
# pg_dump backup (every 6 hours)
0 */6 * * * pg_dump -U gallup_user gallup_strengths | gzip > /backups/gallup-$(date +\%Y\%m\%d-\%H\%M).sql.gz
```

### File Cleanup (Reports)

**Reports accumulate in `output/reports/`** - set up cleanup:

```bash
# Create cleanup script
sudo nano /usr/local/bin/cleanup-gallup-reports.sh
```

**Script content:**
```bash
#!/bin/bash
REPORTS_DIR=/opt/gallup-strengths/output/reports
# Delete reports older than 7 days
find $REPORTS_DIR -name "*.pdf" -mtime +7 -delete
echo "Cleaned up old reports (>7 days)"
```

**Schedule daily:**
```bash
sudo chmod +x /usr/local/bin/cleanup-gallup-reports.sh
sudo crontab -e
0 2 * * * /usr/local/bin/cleanup-gallup-reports.sh >> /var/log/gallup-cleanup.log 2>&1
```

---

## 🚨 Troubleshooting

### Issue 1: Database Lock Errors
**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Cause**: Multiple concurrent writes to SQLite

**Quick Fix:**
1. Verify WAL mode is enabled (already enabled in `database/engine.py:90`)
2. Check concurrent users <20

**Permanent Fix:**
Migrate to PostgreSQL (see Database Migration section)

### Issue 2: 429 Too Many Requests
**Symptom:**
```json
{"error": "Rate limit exceeded: 10 per 1 minute"}
```

**Cause**: Rate limiting triggered (user exceeded 10 submissions/minute)

**Solution**: This is expected behavior. User should wait 1 minute.

**Adjust limits** (if needed):
```python
# api/routes/v4_assessment_sqlalchemy.py
@limiter.limit("20/minute")  # Increase from 10 to 20
```

### Issue 3: Gunicorn Won't Start on Windows
**Symptom:**
```
ModuleNotFoundError: No module named 'fcntl'
```

**Cause**: Gunicorn doesn't support Windows

**Solution:**
Use Uvicorn directly for development on Windows:
```bash
uvicorn src.main.python.api.main:app --host 0.0.0.0 --port 8005
```

**For production**, deploy to Linux (Docker, PaaS, or VPS)

### Issue 4: Import Errors After Deployment
**Symptom:**
```
ModuleNotFoundError: No module named 'core'
```

**Cause**: Incorrect PYTHONPATH or working directory

**Solution:**
```bash
# Set PYTHONPATH before starting
export PYTHONPATH=/opt/gallup-strengths/src/main/python:$PYTHONPATH
gunicorn src.main.python.api.main:app -c gunicorn_conf.py

# Or use absolute imports in gunicorn command
cd /opt/gallup-strengths/src/main/python
gunicorn api.main:app -c ../../gunicorn_conf.py
```

### Issue 5: 502 Bad Gateway (PDF Generation Timeout)
**Symptom**: Nginx returns 502 after ~30 seconds

**Cause**: PDF generation takes longer than proxy timeout

**Solution**: Increase Nginx timeout
```nginx
location / {
    proxy_read_timeout 90s;  # Increase from default 60s
    proxy_connect_timeout 90s;
    proxy_send_timeout 90s;
}
```

---

## 🔒 Security Checklist (Pre-Deployment)

### Before Going Live

- [ ] **Environment Variables**
  - [ ] `.env` file created with production values
  - [ ] `SECRET_KEY` generated with `secrets.token_urlsafe(32)`
  - [ ] `CORS_ORIGINS` set to production domain(s) only
  - [ ] `.env` NOT committed to Git (check `.gitignore`)

- [ ] **Database**
  - [ ] SQLite WAL mode enabled (automatic in code)
  - [ ] Database file has proper permissions (640)
  - [ ] Backup cron job scheduled

- [ ] **Server**
  - [ ] Using Gunicorn (not Uvicorn development server)
  - [ ] Worker count appropriate for CPU (2-4 x cores)
  - [ ] Health check endpoint accessible

- [ ] **Security Headers**
  - [ ] Security headers middleware enabled (automatic)
  - [ ] Rate limiting active (automatic)
  - [ ] HTTPS configured (via reverse proxy)

- [ ] **Monitoring**
  - [ ] Health check monitoring setup
  - [ ] Error tracking (Sentry recommended)
  - [ ] Disk space alerts

- [ ] **Testing**
  - [ ] All tests pass: `pytest src/test/ -v`
  - [ ] Smoke test on staging environment
  - [ ] Load test with expected concurrent users

---

## 📊 Performance Expectations

### Current Configuration

**SQLite + WAL Mode:**
- **Concurrent readers**: ~100 (excellent)
- **Concurrent writers**: ~10-20 (acceptable for MVP)
- **API latency**: <100ms (non-PDF endpoints)
- **PDF generation**: 0.5-2s per report
- **Memory usage**: ~150MB base + 50MB per worker

### Scaling Triggers

**Migrate to PostgreSQL when:**
- Concurrent users >20
- Database lock errors appear
- Need high availability/replication

**Add load balancer when:**
- Single server >80% CPU
- Need zero-downtime deployments
- Geographic distribution required

---

## 🎯 Deployment Phases

### Phase 1: MVP Launch (<50 users)
- **Platform**: Render/Railway free tier
- **Database**: SQLite + WAL
- **Storage**: Local volume
- **Monitoring**: Platform logs + health check
- **Cost**: $0-7/month

### Phase 2: Production (100-500 users)
- **Platform**: Render/Railway paid OR VPS
- **Database**: PostgreSQL (managed)
- **Storage**: S3/Spaces (optional)
- **Monitoring**: Sentry + metrics
- **Cost**: $20-50/month

### Phase 3: Scale (>500 users)
- **Platform**: AWS/GCP/Azure
- **Database**: PostgreSQL with read replicas
- **Storage**: CDN + object storage
- **Monitoring**: Full APM (Datadog/New Relic)
- **Cost**: $100-500/month

---

## 🔄 Zero-Downtime Deployment

### With PostgreSQL (Recommended)

**Strategy**: Rolling deployment

```bash
# 1. Run database migrations first
alembic upgrade head

# 2. Deploy new version (platform handles rolling)
git push origin main  # On Render/Railway

# 3. Monitor health
watch -n 5 'curl -s http://your-app.com/api/system/health | jq .status'

# 4. Rollback if needed
git revert HEAD && git push origin main
```

### With SQLite (Limited)

**Strategy**: Quick restart (acceptable for MVP)

```bash
# 1. Backup database
sqlite3 data/gallup_strengths.db ".backup data/backup-pre-deploy.db"

# 2. Stop service
sudo systemctl stop gallup-assessment

# 3. Update code
git pull origin main

# 4. Restart service
sudo systemctl start gallup-assessment

# Downtime: ~10 seconds
```

---

## 📞 Emergency Procedures

### Rollback Process

**If deployment fails:**
```bash
# 1. Identify last working commit
git log --oneline -5

# 2. Revert to working version
git revert <bad-commit-sha>
git push origin main

# 3. Or hard reset (use with caution)
git reset --hard <good-commit-sha>
git push --force origin main  # Only if necessary
```

### Database Restore

**SQLite:**
```bash
# Stop application
sudo systemctl stop gallup-assessment

# Restore from backup
cp /backups/gallup-db/db-<timestamp>.db data/gallup_strengths.db

# Restart application
sudo systemctl start gallup-assessment
```

**PostgreSQL:**
```bash
# Drop and recreate database
sudo -u postgres psql
DROP DATABASE gallup_strengths;
CREATE DATABASE gallup_strengths;
\q

# Restore from backup
gunzip < /backups/gallup-<timestamp>.sql.gz | psql -U gallup_user gallup_strengths
```

---

## 🎯 Post-Deployment Validation

### Smoke Tests (Run after every deployment)

```bash
# 1. Health check
curl -f http://your-app.com/api/system/health || echo "FAILED: Health check"

# 2. Get assessment blocks
curl -f http://your-app.com/api/assessment/blocks || echo "FAILED: Blocks endpoint"

# 3. Submit test assessment (requires valid payload)
# See API_EXAMPLES.md for full request

# 4. Check error logs
# Docker: docker logs gallup-app --tail=50
# Systemd: journalctl -u gallup-assessment -n 50
```

### Load Testing

**Using Apache Bench:**
```bash
# Install ab
sudo apt install apache2-utils -y

# Test 100 requests, 10 concurrent
ab -n 100 -c 10 http://your-app.com/api/system/health

# Test assessment endpoint (POST requires payload file)
ab -n 50 -c 5 -p test-payload.json -T application/json \
   http://your-app.com/api/assessment/submit
```

**Expected results:**
- **Requests/sec**: >50 (health check)
- **Failed requests**: 0
- **Time per request**: <100ms (non-PDF endpoints)

---

## 📚 Additional Resources

- **API Documentation**: `/api/docs` (Swagger UI)
- **API Examples**: `API_EXAMPLES.md`
- **Architecture**: `ARCHITECTURE.md`
- **Development Guide**: `CLAUDE.md`
- **Project Board**: GitHub Projects (if configured)

---

## 🤝 Support

**Issues**: Report at https://github.com/Zenobia000/gallup-strengths-assessment/issues

**Questions**: Check existing documentation first, then open a discussion

---

## 🏁 Quick Reference

```bash
# Development
uvicorn src.main.python.api.main:app --reload

# Production (Docker)
docker-compose up -d

# Production (Manual)
gunicorn src.main.python.api.main:app -c gunicorn_conf.py

# Health Check
curl http://localhost:8005/api/system/health

# View Logs
docker logs -f gallup-app                    # Docker
journalctl -u gallup-assessment -f           # Systemd

# Database Backup
sqlite3 data/gallup_strengths.db ".backup backup.db"

# Run Tests
pytest src/test/ -v
```

---

**Deployment Philosophy**: "Deploy early, deploy often, monitor always." - DevOps Wisdom

**Linus says**: "Release early. Release often. And listen to your customers." 🚀
