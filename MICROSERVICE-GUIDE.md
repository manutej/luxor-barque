# BARQUE Microservice Deployment Guide

**FastAPI-based REST API for PDF Generation and Email Delivery**

---

## Overview

BARQUE Microservice provides a REST API wrapper around the existing BARQUE CLI, enabling:

- **API-first PDF generation** from markdown
- **Email delivery** with attachments
- **Combined operations** (generate + send in one call)
- **Docker deployment** for easy scaling
- **OpenAPI documentation** (Swagger UI)

**Important**: The CLI remains completely untouched and continues to work in production!

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 BARQUE Microservice                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐                                       │
│  │  FastAPI     │  ← HTTP REST API                     │
│  │  (barque_    │                                       │
│  │   service.py)│                                       │
│  └──────┬───────┘                                       │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────────────────┐                      │
│  │   BARQUE Core (Unchanged)     │                      │
│  │   ├─ generator.py            │                      │
│  │   ├─ email.py                │                      │
│  │   ├─ config.py               │                      │
│  │   └─ metadata.py             │                      │
│  └──────────────────────────────┘                      │
│                                                          │
│  CLI (barque/cli/commands.py) ← Untouched!             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Key Point**: The microservice imports and uses BARQUE core modules directly. The CLI is never modified or called.

---

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/manutej/luxor-barque.git
cd luxor-barque

# 2. Create environment file
cp .env.example .env
nano .env  # Add your RESEND_API_KEY

# 3. Start service
docker-compose up -d

# 4. Check health
curl http://localhost:8000/health

# 5. View API docs
open http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# 1. Install dependencies
pip install -r requirements-service.txt
pip install -e .

# 2. Set environment variables
export RESEND_API_KEY="re_xxxxxxxxxxxxx"
export POP_FROM="reports@company.com"

# 3. Start service
uvicorn barque_service:app --reload --port 8000

# 4. Access docs
open http://localhost:8000/docs
```

---

## API Endpoints

### GET `/` - API Information

```bash
curl http://localhost:8000/
```

Response:
```json
{
  "success": true,
  "message": "BARQUE Microservice API",
  "data": {
    "version": "1.0.0",
    "barque_version": "2.0.0",
    "docs": "/docs",
    "health": "/health"
  }
}
```

### GET `/health` - Health Check

```bash
curl http://localhost:8000/health
```

### POST `/generate` - Generate PDF

Generate PDF from markdown content.

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "# Monthly Report\n\nQ4 results are excellent!",
    "theme": "both",
    "filename": "monthly-report"
  }'
```

Response:
```json
{
  "success": true,
  "message": "PDF generated successfully",
  "data": {
    "job_id": "a1b2c3d4",
    "files": [
      {
        "filename": "monthly-report-light.pdf",
        "url": "/download/a1b2c3d4/monthly-report-light.pdf",
        "size_bytes": 152340
      },
      {
        "filename": "monthly-report-dark.pdf",
        "url": "/download/a1b2c3d4/monthly-report-dark.pdf",
        "size_bytes": 153210
      }
    ],
    "metadata": {
      "title": "Monthly Report",
      "word_count": 245,
      "sections": 5
    }
  }
}
```

### POST `/send-email` - Send Email with Attachments

Upload files and send via email.

```bash
curl -X POST http://localhost:8000/send-email \
  -F "files=@report.pdf" \
  -F "to=user@example.com" \
  -F "subject=Monthly Report" \
  -F "provider=resend"
```

### POST `/generate-and-send` - Generate PDF and Email

**Most useful endpoint** - combines generation and email delivery.

```bash
curl -X POST http://localhost:8000/generate-and-send \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "# Q4 Report\n\n## Revenue\n$1.2M (+15%)\n\n## Customers\n1,200 new accounts",
    "to": ["ceo@company.com", "cfo@company.com"],
    "subject": "Q4 Financial Report",
    "theme": "both",
    "provider": "resend"
  }'
```

Response:
```json
{
  "success": true,
  "message": "PDF generated and email sent successfully",
  "data": {
    "job_id": "e5f6g7h8",
    "recipients": ["ceo@company.com", "cfo@company.com"],
    "pdf_files": ["document-e5f6g7h8-light.pdf", "document-e5f6g7h8-dark.pdf"],
    "metadata": {
      "title": "Q4 Report",
      "word_count": 125
    }
  }
}
```

---

## Integration Examples

### Python

```python
import requests

# Generate and send report
response = requests.post(
    "http://localhost:8000/generate-and-send",
    json={
        "markdown_content": "# Daily Report\n\nMetrics...",
        "to": ["team@company.com"],
        "subject": "Daily Report - 2025-11-01",
        "theme": "light"
    }
)

if response.json()["success"]:
    print("Report sent successfully!")
```

### cURL

```bash
#!/bin/bash
# daily-report.sh

# Read markdown from file
MARKDOWN=$(cat daily-report.md)

# Send via API
curl -X POST http://localhost:8000/generate-and-send \
  -H "Content-Type: application/json" \
  -d "{
    \"markdown_content\": \"$MARKDOWN\",
    \"to\": [\"team@company.com\"],
    \"subject\": \"Daily Report - $(date +%Y-%m-%d)\",
    \"theme\": \"both\"
  }"
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function sendReport(markdown, recipients) {
  const response = await axios.post('http://localhost:8000/generate-and-send', {
    markdown_content: markdown,
    to: recipients,
    subject: 'Automated Report',
    theme: 'both',
    provider: 'resend'
  });

  return response.data;
}

// Usage
sendReport('# Report\n\nContent...', ['user@example.com'])
  .then(result => console.log('Success:', result))
  .catch(error => console.error('Error:', error));
```

---

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t barque-api:latest .

# Run container
docker run -d \
  --name barque-service \
  -p 8000:8000 \
  -e RESEND_API_KEY="re_xxxxx" \
  -e POP_FROM="reports@company.com" \
  barque-api:latest

# Check logs
docker logs barque-service

# Check health
curl http://localhost:8000/health
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f barque-api

# Stop services
docker-compose down

# Restart
docker-compose restart barque-api
```

### Production Deployment with Nginx

```bash
# Start with nginx reverse proxy
docker-compose --profile production up -d

# Now accessible via http://localhost (port 80)
```

---

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `RESEND_API_KEY` | Resend API key | - | Yes (if using Resend) |
| `POP_FROM` | Default sender email | - | Recommended |
| `POP_SMTP_HOST` | SMTP server | - | Yes (if using SMTP) |
| `POP_SMTP_PORT` | SMTP port | 587 | No |
| `POP_SMTP_USERNAME` | SMTP username | - | Yes (if using SMTP) |
| `POP_SMTP_PASSWORD` | SMTP password | - | Yes (if using SMTP) |
| `LOG_LEVEL` | Logging level | INFO | No |
| `WORKERS` | Worker processes | 4 | No |

---

## Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: barque-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: barque-api
  template:
    metadata:
      labels:
        app: barque-api
    spec:
      containers:
      - name: barque
        image: barque-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: RESEND_API_KEY
          valueFrom:
            secretKeyRef:
              name: barque-secrets
              key: resend-api-key
        - name: POP_FROM
          value: "reports@company.com"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: barque-api
spec:
  selector:
    app: barque-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Create Secret

```bash
kubectl create secret generic barque-secrets \
  --from-literal=resend-api-key="re_xxxxxxxxxxxxx"
```

### Deploy

```bash
kubectl apply -f barque-deployment.yaml
kubectl get pods -l app=barque-api
kubectl logs -l app=barque-api
```

---

## Integration with LUMOS/LUMINA

### LUMOS Integration (AI-Generated Reports)

```python
# In LUMOS workflow
import requests

def generate_ai_report(analysis_result):
    """Generate PDF from AI analysis and email it"""

    # AI generates markdown report
    markdown = f"""# AI Analysis Report

## Summary
{analysis_result.summary}

## Key Findings
{analysis_result.findings}

## Recommendations
{analysis_result.recommendations}
"""

    # Send via BARQUE API
    response = requests.post(
        "http://barque-api:8000/generate-and-send",
        json={
            "markdown_content": markdown,
            "to": ["stakeholders@company.com"],
            "subject": f"AI Analysis - {analysis_result.date}",
            "theme": "both"
        }
    )

    return response.json()
```

### LUMINA Integration (Dashboard Exports)

```python
# In LUMINA dashboard exporter
import requests

def export_dashboard(dashboard_data):
    """Export dashboard as PDF and email"""

    # Generate markdown from dashboard
    markdown = dashboard_data.to_markdown()

    # Send via BARQUE API
    response = requests.post(
        "http://barque-api:8000/generate-and-send",
        json={
            "markdown_content": markdown,
            "to": ["executives@company.com"],
            "subject": "Weekly Dashboard Report",
            "theme": "light"  # Light theme for printing
        }
    )

    return response.json()
```

---

## API Documentation

### Swagger UI (Interactive)

Access at: `http://localhost:8000/docs`

Features:
- Interactive API testing
- Request/response examples
- Schema definitions
- Authentication testing

### ReDoc (Documentation)

Access at: `http://localhost:8000/redoc`

Features:
- Clean, readable documentation
- Code examples
- Schema explorer
- Downloadable OpenAPI spec

---

## Monitoring and Logging

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Docker healthcheck (automatic)
docker ps  # Shows "healthy" status
```

### Logs

```bash
# Docker logs
docker logs barque-service -f

# Docker Compose logs
docker-compose logs -f barque-api

# Kubernetes logs
kubectl logs -f -l app=barque-api
```

### Metrics (Future Enhancement)

Consider adding:
- Prometheus metrics endpoint
- Request duration tracking
- Error rate monitoring
- Resource usage metrics

---

## Security Best Practices

### 1. Environment Variables

✅ **DO**:
- Use Kubernetes secrets
- Use Docker secrets
- Use AWS Secrets Manager
- Rotate API keys regularly

❌ **DON'T**:
- Commit `.env` files
- Hardcode credentials
- Share API keys in logs

### 2. Network Security

```yaml
# docker-compose.yml with network isolation
services:
  barque-api:
    networks:
      - internal
    # Only expose to nginx, not public

  nginx:
    networks:
      - internal
      - public
    ports:
      - "443:443"  # HTTPS only

networks:
  internal:
    internal: true
  public:
```

### 3. API Authentication (Future Enhancement)

```python
# Add API key authentication
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@app.post("/generate-and-send")
async def generate_and_send(
    request: GenerateAndSendRequest,
    api_key: str = Depends(api_key_header)
):
    verify_api_key(api_key)
    # ... rest of endpoint
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker logs barque-service

# Common issues:
# 1. Port already in use
docker ps  # Check if port 8000 is occupied

# 2. Missing environment variables
docker exec barque-service env | grep RESEND
```

### PDF Generation Fails

```bash
# Check pandoc installation
docker exec barque-service pandoc --version

# Check weasyprint
docker exec barque-service python -c "import weasyprint; print('OK')"
```

### Email Not Sending

```bash
# Check Pop installation
docker exec barque-service pop --version

# Check environment variables
docker exec barque-service env | grep -E "RESEND|POP"

# Test manually
docker exec -it barque-service bash
echo "Test" | pop --to test@example.com --subject "Test"
```

---

## Performance Optimization

### Scaling

```bash
# Scale with Docker Compose
docker-compose up -d --scale barque-api=3

# Load balancer will distribute requests
```

### Caching (Future Enhancement)

```python
# Add Redis caching for generated PDFs
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="barque-cache")
```

---

## CLI Compatibility

**IMPORTANT**: The CLI is completely untouched!

```bash
# CLI continues to work exactly as before
barque generate report.md
barque send report.md --to user@example.com
barque batch docs/

# Microservice provides additional API access
# Both can run simultaneously without conflicts
```

---

## Next Steps

1. **Deploy to staging** environment
2. **Test all endpoints** with real data
3. **Set up monitoring** (Prometheus + Grafana)
4. **Add authentication** (API keys or OAuth)
5. **Implement rate limiting**
6. **Add request validation**
7. **Set up CI/CD pipeline**
8. **Load testing** (Locust or k6)

---

## Support

- **GitHub Issues**: https://github.com/manutej/luxor-barque/issues
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

**BARQUE Microservice - Production-Ready REST API** 🚀

*CLI untouched, API-first access, Docker-ready deployment*
