# 📡 API Examples - Gallup Strengths Assessment v4.0

**Base URL**: `http://localhost:8005` (development) or `https://your-domain.com` (production)

**Authentication**: None (currently open API)

**Rate Limits**:
- Global: 60 requests/minute per IP
- Submit endpoint: 10 requests/minute per IP

---

## Table of Contents

1. [Health Check](#1-health-check)
2. [Get Assessment Blocks](#2-get-assessment-blocks)
3. [Submit Assessment](#3-submit-assessment)
4. [Get Results](#4-get-results)
5. [Generate Report](#5-generate-report)
6. [Error Handling](#error-handling)

---

## 1. Health Check

**Check system status and database connectivity**

### Request
```bash
curl -X GET http://localhost:8005/api/system/health
```

### Response (Success - 200)
```json
{
  "status": "healthy",
  "timestamp": "2025-10-03T10:30:00.123456",
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

### Response (Unhealthy - 200)
```json
{
  "status": "unhealthy",
  "timestamp": "2025-10-03T10:30:00.123456",
  "version": "1.0.0",
  "database_status": "error",
  "error": "Database connection failed: ..."
}
```

### Use Cases
- Uptime monitoring
- Pre-deployment validation
- Health dashboard integration

---

## 2. Get Assessment Blocks

**Generate Thurstonian IRT forced-choice quartet blocks**

### Request
```bash
curl -X GET 'http://localhost:8005/api/assessment/blocks?block_count=10&randomize=true' \
  -H 'Content-Type: application/json'
```

### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `consent_id` | string | No | null | Consent ID (creates anonymous session if omitted) |
| `block_count` | integer | No | 10 | Number of blocks (5-20) |
| `randomize` | boolean | No | true | Randomize block order |

### Response (Success - 200)
```json
{
  "session_id": "v4_a1b2c3d4e5f6",
  "blocks": [
    {
      "block_id": 1,
      "statements": [
        {
          "id": "T1-S001",
          "text": "我喜歡制定詳細的計劃並按部就班執行",
          "dimension": "T1"
        },
        {
          "id": "T2-S012",
          "text": "我重視工作的精準度和完整性",
          "dimension": "T2"
        },
        {
          "id": "T3-S023",
          "text": "我經常提出創新的想法和解決方案",
          "dimension": "T3"
        },
        {
          "id": "T4-S034",
          "text": "我擅長分析複雜問題的根本原因",
          "dimension": "T4"
        }
      ]
    }
  ],
  "total_blocks": 10,
  "instructions": "請從以下4個選項中，選擇最像你和最不像你的選項"
}
```

### Validation Rules
- `block_count`: Must be between 5 and 20
- Each block contains exactly 4 statements
- Statements are balanced across T1-T12 dimensions

### Use Cases
- Start new assessment session
- Generate practice blocks for demo

---

## 3. Submit Assessment

**Submit user responses and calculate scores**

### Request
```bash
curl -X POST http://localhost:8005/api/assessment/submit \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "v4_a1b2c3d4e5f6",
    "responses": [
      {
        "block_id": 1,
        "most_like_index": 0,
        "least_like_index": 2,
        "response_time_ms": 3500
      },
      {
        "block_id": 2,
        "most_like_index": 1,
        "least_like_index": 3,
        "response_time_ms": 4200
      }
    ],
    "completion_time_seconds": 125.5
  }'
```

### Request Body Schema
```typescript
{
  session_id: string,           // Required: Session ID from /blocks
  responses: [                  // Required: At least 1 response
    {
      block_id: number,         // Required: >= 1
      most_like_index: number,  // Required: 0-3
      least_like_index: number, // Required: 0-3, must differ from most_like
      response_time_ms?: number // Optional: >= 0
    }
  ],
  completion_time_seconds?: number  // Optional: >= 0
}
```

### Validation Rules
- `session_id`: Must exist and not be expired
- `block_id`: Must be >= 1
- `most_like_index` and `least_like_index`: Must be 0-3 and **different**
- No duplicate `block_id` in responses
- `completion_time_seconds`: If provided, must be reasonable (2-60s per response)

### Response (Success - 200)
```json
{
  "session_id": "v4_a1b2c3d4e5f6",
  "scores": {
    "T1": 75.3,
    "T2": 82.1,
    "T3": 45.7,
    "T4": 68.9,
    "T5": 55.2,
    "T6": 71.4,
    "T7": 60.8,
    "T8": 53.6,
    "T9": 77.5,
    "T10": 49.1,
    "T11": 58.3,
    "T12": 70.2
  },
  "message": "Assessment completed successfully. Scores calculated using Thurstonian IRT model.",
  "analysis_complete": true
}
```

### Response (Error - 400: Validation Error)
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "responses", 0],
      "msg": "most_like_index (2) and least_like_index (2) must be different",
      "input": {...}
    }
  ]
}
```

### Response (Error - 404: Session Not Found)
```json
{
  "detail": "Session v4_invalid_session not found"
}
```

### Response (Error - 429: Rate Limit)
```json
{
  "error": "Rate limit exceeded: 10 per 1 minute"
}
```

### Use Cases
- Complete assessment submission
- Calculate talent scores

---

## 4. Get Results

**Retrieve full assessment results with archetype analysis**

### Request
```bash
curl -X GET http://localhost:8005/api/assessment/results/v4_a1b2c3d4e5f6
```

### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Session ID from previous steps |

### Response (Success - 200)
```json
{
  "session_id": "v4_a1b2c3d4e5f6",
  "t_scores": {
    "T1": 75.3,
    "T2": 82.1,
    "T3": 45.7,
    "T4": 68.9,
    "T5": 55.2,
    "T6": 71.4,
    "T7": 60.8,
    "T8": 53.6,
    "T9": 77.5,
    "T10": 49.1,
    "T11": 58.3,
    "T12": 70.2
  },
  "percentile_scores": {
    "T1": 78,
    "T2": 85,
    "T3": 42,
    ...
  },
  "talent_classification": {
    "dominant": ["T2", "T9", "T1"],
    "supporting": ["T12", "T6", "T4"],
    "lesser": ["T3", "T10", "T11"]
  },
  "archetype_analysis": {
    "primary_archetype": "GUARDIAN",
    "archetype_name": "組織守護者",
    "confidence": 0.87,
    "description": "...",
    "career_suggestions": [...]
  },
  "metadata": {
    "algorithm_version": "4.0.0-alpha",
    "calibration_version": "v4_pilot_2025",
    "computed_at": "2025-10-03T10:35:00",
    "computation_time_ms": 25.3
  }
}
```

### Response (Error - 404: Results Not Found)
```json
{
  "detail": "Assessment results not found for session v4_a1b2c3d4e5f6"
}
```

### Use Cases
- Display results to user
- Download results data
- Feed into recommendation engine

---

## 5. Generate Report

**Generate detailed PDF report**

### Request
```bash
curl -X POST http://localhost:8005/api/reports/generate/v4_a1b2c3d4e5f6 \
  -H 'Content-Type: application/json'
```

### Response (Success - 200)
```json
{
  "session_id": "v4_a1b2c3d4e5f6",
  "report_generated": true,
  "report_url": "/static/reports/v4_a1b2c3d4e5f6_report.pdf",
  "generated_at": "2025-10-03T10:40:00",
  "expires_at": "2025-10-10T10:40:00"
}
```

### Response (Error - 404: No Results)
```json
{
  "detail": "No assessment results found for session v4_a1b2c3d4e5f6. Please complete assessment first."
}
```

### Download Report
```bash
# After generation, download PDF
curl -O http://localhost:8005/static/reports/v4_a1b2c3d4e5f6_report.pdf
```

### Use Cases
- Generate PDF for user download
- Create shareable reports
- Archive assessment results

---

## Error Handling

### Standard Error Response Format

All errors follow this structure:
```json
{
  "detail": "Human-readable error message"
}
```

Or for validation errors:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "field_name"],
      "msg": "Validation error message",
      "input": {...}
    }
  ]
}
```

### HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid input, validation failed |
| 404 | Not Found | Session/resource doesn't exist |
| 422 | Unprocessable Entity | Pydantic validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error (bug or system issue) |

### Common Error Scenarios

#### Validation Error Example
```bash
# Invalid request: same most_like and least_like index
curl -X POST http://localhost:8005/api/assessment/submit \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "v4_test",
    "responses": [{
      "block_id": 1,
      "most_like_index": 2,
      "least_like_index": 2  # ERROR: Same as most_like
    }]
  }'
```

**Response (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "responses", 0],
      "msg": "most_like_index (2) and least_like_index (2) must be different"
    }
  ]
}
```

#### Rate Limit Error Example
```bash
# Send 11 submissions in 1 minute (exceeds 10/minute limit)
for i in {1..11}; do
  curl -X POST http://localhost:8005/api/assessment/submit -d '{...}'
done
```

**Response (429):**
```json
{
  "error": "Rate limit exceeded: 10 per 1 minute"
}
```

---

## Complete Workflow Example

### Full Assessment Flow (Bash Script)

```bash
#!/bin/bash
BASE_URL="http://localhost:8005"

echo "=== Step 1: Health Check ==="
curl -s "$BASE_URL/api/system/health" | jq '.status'

echo "\n=== Step 2: Get Assessment Blocks ==="
BLOCKS_RESPONSE=$(curl -s "$BASE_URL/api/assessment/blocks?block_count=10")
SESSION_ID=$(echo $BLOCKS_RESPONSE | jq -r '.session_id')
echo "Session ID: $SESSION_ID"

echo "\n=== Step 3: Simulate User Responses ==="
# In real usage, user answers through frontend
# Here we simulate 10 responses
SUBMIT_PAYLOAD=$(cat <<EOF
{
  "session_id": "$SESSION_ID",
  "responses": [
    {"block_id": 1, "most_like_index": 0, "least_like_index": 2, "response_time_ms": 3500},
    {"block_id": 2, "most_like_index": 1, "least_like_index": 3, "response_time_ms": 4200},
    {"block_id": 3, "most_like_index": 2, "least_like_index": 0, "response_time_ms": 3800},
    {"block_id": 4, "most_like_index": 3, "least_like_index": 1, "response_time_ms": 4500},
    {"block_id": 5, "most_like_index": 0, "least_like_index": 3, "response_time_ms": 3200},
    {"block_id": 6, "most_like_index": 1, "least_like_index": 2, "response_time_ms": 4100},
    {"block_id": 7, "most_like_index": 2, "least_like_index": 1, "response_time_ms": 3900},
    {"block_id": 8, "most_like_index": 3, "least_like_index": 0, "response_time_ms": 3700},
    {"block_id": 9, "most_like_index": 0, "least_like_index": 1, "response_time_ms": 4300},
    {"block_id": 10, "most_like_index": 1, "least_like_index": 3, "response_time_ms": 3600}
  ],
  "completion_time_seconds": 125.5
}
EOF
)

echo "\n=== Step 4: Submit Assessment ==="
SCORE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/assessment/submit" \
  -H 'Content-Type: application/json' \
  -d "$SUBMIT_PAYLOAD")
echo $SCORE_RESPONSE | jq '.'

echo "\n=== Step 5: Get Full Results ==="
curl -s "$BASE_URL/api/assessment/results/$SESSION_ID" | jq '.'

echo "\n=== Step 6: Generate PDF Report ==="
curl -s -X POST "$BASE_URL/api/reports/generate/$SESSION_ID" | jq '.report_url'

echo "\n✅ Complete workflow finished!"
```

### Python Example

```python
import requests
import json

BASE_URL = "http://localhost:8005"

# Step 1: Health Check
health = requests.get(f"{BASE_URL}/api/system/health").json()
print(f"System Status: {health['status']}")

# Step 2: Get Blocks
blocks_response = requests.get(
    f"{BASE_URL}/api/assessment/blocks",
    params={"block_count": 10, "randomize": True}
).json()

session_id = blocks_response["session_id"]
print(f"Session ID: {session_id}")
print(f"Total Blocks: {blocks_response['total_blocks']}")

# Step 3: Submit Responses (simulated user input)
responses = [
    {
        "block_id": i + 1,
        "most_like_index": i % 4,
        "least_like_index": (i + 2) % 4,
        "response_time_ms": 3000 + (i * 100)
    }
    for i in range(10)
]

submit_payload = {
    "session_id": session_id,
    "responses": responses,
    "completion_time_seconds": 125.5
}

# Step 4: Submit Assessment
score_response = requests.post(
    f"{BASE_URL}/api/assessment/submit",
    json=submit_payload
).json()

print(f"\n=== Talent Scores ===")
for talent, score in score_response["scores"].items():
    print(f"{talent}: {score:.1f}")

# Step 5: Get Full Results
results = requests.get(f"{BASE_URL}/api/assessment/results/{session_id}").json()
print(f"\nPrimary Archetype: {results['archetype_analysis']['archetype_name']}")

# Step 6: Generate Report
report = requests.post(f"{BASE_URL}/api/reports/generate/{session_id}").json()
print(f"\nReport URL: {BASE_URL}{report['report_url']}")
```

---

## Testing & Validation

### Validate Endpoint Response

```bash
# Test health check returns healthy status
curl -s http://localhost:8005/api/system/health | jq -e '.status == "healthy"' && echo "✅ PASS" || echo "❌ FAIL"

# Test blocks returns expected number
curl -s 'http://localhost:8005/api/assessment/blocks?block_count=5' | jq -e '.total_blocks == 5' && echo "✅ PASS" || echo "❌ FAIL"

# Test rate limiting (should fail on 11th request)
for i in {1..11}; do
  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8005/api/assessment/submit -d '{}')
  STATUS=$(echo "$RESPONSE" | tail -1)
  if [ $i -le 10 ]; then
    echo "Request $i: Expected 400/422, Got $STATUS"
  else
    echo "Request $i: Expected 429, Got $STATUS"
    [ "$STATUS" == "429" ] && echo "✅ Rate limiting works!" || echo "❌ Rate limiting failed"
  fi
  sleep 1
done
```

### Integration Test Example

```python
import pytest
import requests

BASE_URL = "http://localhost:8005"

def test_full_assessment_workflow():
    """Test complete assessment flow from blocks to report"""

    # Step 1: Get blocks
    blocks_resp = requests.get(f"{BASE_URL}/api/assessment/blocks")
    assert blocks_resp.status_code == 200

    session_id = blocks_resp.json()["session_id"]
    total_blocks = blocks_resp.json()["total_blocks"]

    # Step 2: Submit responses
    responses = [
        {
            "block_id": i + 1,
            "most_like_index": 0,
            "least_like_index": 2
        }
        for i in range(total_blocks)
    ]

    submit_resp = requests.post(
        f"{BASE_URL}/api/assessment/submit",
        json={
            "session_id": session_id,
            "responses": responses,
            "completion_time_seconds": 120.0
        }
    )

    assert submit_resp.status_code == 200
    scores = submit_resp.json()["scores"]
    assert len(scores) == 12  # T1-T12

    # Step 3: Get results
    results_resp = requests.get(f"{BASE_URL}/api/assessment/results/{session_id}")
    assert results_resp.status_code == 200

    results = results_resp.json()
    assert "archetype_analysis" in results
    assert "talent_classification" in results

    # Step 4: Generate report
    report_resp = requests.post(f"{BASE_URL}/api/reports/generate/{session_id}")
    assert report_resp.status_code == 200
    assert report_resp.json()["report_generated"] == True

    print("✅ Full workflow test PASSED")
```

---

## Security Headers in Response

Every API response includes security headers:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Timestamp: 2025-10-03T10:30:00.123456
X-API-Version: 1.0.0
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; ...
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

## API Versioning

**Current version**: v1.0.0

**Future versions** will be namespaced:
- `/api/v1/...` - Current stable
- `/api/v2/...` - Future enhancements (H-MIRT)

**Migration strategy**: Old versions supported for 6 months after new version release.

---

## Rate Limiting Details

### Current Limits

| Endpoint | Limit | Window | Reason |
|----------|-------|--------|--------|
| **Global** | 60 requests | 1 minute | Normal usage |
| `/assessment/submit` | 10 requests | 1 minute | Prevent abuse |
| Other endpoints | Inherit global | 1 minute | Default |

### Checking Rate Limit Status

**Response headers include:**
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1696332000
```

### Handling Rate Limits (Client-Side)

```python
import time
import requests

def submit_with_retry(url, payload, max_retries=3):
    """Submit with automatic retry on rate limit"""
    for attempt in range(max_retries):
        response = requests.post(url, json=payload)

        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            continue

        return response

    raise Exception("Max retries exceeded")
```

---

## Postman Collection

### Import to Postman

1. Create new collection: "Gallup Strengths API"
2. Add environment variables:
   - `base_url`: `http://localhost:8005`
   - `session_id`: (will be set dynamically)

3. Add requests:
   - Health Check (GET)
   - Get Blocks (GET) - Save `session_id` to variable
   - Submit Assessment (POST) - Use saved `session_id`
   - Get Results (GET)
   - Generate Report (POST)

### Export collection
```json
{
  "info": {
    "name": "Gallup Strengths API v4.0",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/system/health"
      }
    }
    // ... other endpoints
  ]
}
```

---

## 🎓 Best Practices

### 1. Always Check Health First
```bash
# Before any operation
curl http://your-app.com/api/system/health
```

### 2. Store session_id Securely
- Don't log session IDs in client-side code
- Use HTTPS in production
- Set reasonable session expiry (currently 2 hours)

### 3. Handle Rate Limits Gracefully
- Implement exponential backoff
- Show user-friendly messages ("Please wait 1 minute")
- Don't retry immediately

### 4. Validate Responses Client-Side
- Check indices before submission
- Ensure all blocks answered
- Validate completion time

---

**Documentation Philosophy**: "Examples speak louder than specifications." - Show working code, not just schemas.

**Linus says**: "Talk is cheap. Show me the curl commands." 🚀
