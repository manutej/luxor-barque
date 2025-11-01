# BARQUE Configuration Guide

**Production-Ready Configuration Management**

---

## Overview

BARQUE uses a hierarchical configuration system that loads settings from multiple sources with clear precedence rules. This ensures security (no secrets in git) while maintaining flexibility.

## Configuration Precedence

Settings are loaded in this order (later sources override earlier ones):

1. **Default values** (hardcoded in code)
2. **Global config file** (`~/.config/barque/email.yaml` or `~/.barque/email.yaml`)
3. **Project config file** (`.barque/email.yaml` in your project)
4. **Environment variables** (highest priority)
5. **Command-line arguments** (overrides everything)

---

## Quick Start

### Option 1: Environment Variables (Simplest)

```bash
# Resend API (recommended)
export RESEND_API_KEY="re_xxxxxxxxxxxxx"
export POP_FROM="reports@company.com"

# OR SMTP
export POP_SMTP_HOST="smtp.gmail.com"
export POP_SMTP_PORT="587"
export POP_SMTP_USERNAME="your-email@gmail.com"
export POP_SMTP_PASSWORD="your-app-password"
export POP_FROM="your-email@gmail.com"
```

### Option 2: Config File (Recommended for Projects)

```bash
# Copy example config
cp .barque/email.example.yaml .barque/email.yaml

# Edit with your credentials
nano .barque/email.yaml

# ⚠️ IMPORTANT: Never commit email.yaml!
# It's already in .gitignore
```

---

## Configuration File Format

### Location Options

BARQUE searches for config files in this order:

1. `./barque/email.yaml` (project-specific, highest priority file-based)
2. `~/.config/barque/email.yaml` (user-specific)
3. `~/.barque/email.yaml` (user-specific, legacy location)

### Example: `.barque/email.yaml`

```yaml
# Email provider: "resend" or "smtp"
provider: "resend"

# Resend API Configuration
resend:
  api_key: "re_xxxxxxxxxxxxx"  # Get from https://resend.com/api-keys

# SMTP Configuration (alternative to Resend)
smtp:
  host: "smtp.gmail.com"
  port: 587
  username: "your-email@gmail.com"
  password: "your-app-password"  # Use app-specific password for Gmail
  use_tls: true

# Default sender settings
defaults:
  from_email: "reports@company.com"
  from_name: "BARQUE Report System"
  signature: |
    ---
    Automated by BARQUE v2.0.0
    https://github.com/manutej/luxor-barque

# Email delivery options
delivery:
  max_retries: 3
  retry_delay_seconds: 5
  retry_exponential_backoff: true
  rate_limit: 60  # emails per minute
  max_attachment_size_mb: 25
  max_attachments: 10
```

---

## Environment Variables

### Resend API

```bash
# API Key (required for Resend)
export RESEND_API_KEY="re_xxxxxxxxxxxxx"

# Optional defaults
export POP_FROM="reports@company.com"
export POP_SIGNATURE="---
Sent with BARQUE
"
```

### SMTP

```bash
# SMTP Configuration (required for SMTP)
export POP_SMTP_HOST="smtp.gmail.com"
export POP_SMTP_PORT="587"
export POP_SMTP_USERNAME="your-email@gmail.com"
export POP_SMTP_PASSWORD="your-app-password"

# Optional defaults
export POP_FROM="your-email@gmail.com"
export POP_SIGNATURE="---
Sent with BARQUE
"
```

### Making Environment Variables Persistent

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# BARQUE Email Configuration
export RESEND_API_KEY="re_xxxxxxxxxxxxx"
export POP_FROM="reports@company.com"

# Then reload shell
source ~/.zshrc
```

---

## Security Best Practices

### ✅ DO

1. **Use environment variables for secrets** in production
2. **Use config files for project settings** (non-sensitive)
3. **Keep `.barque/email.yaml` in `.gitignore`**
4. **Use app-specific passwords** for Gmail/SMTP
5. **Commit `.barque/email.example.yaml`** for documentation
6. **Use secret management** (Vault, AWS Secrets Manager) in production

### ❌ DON'T

1. **Never commit real credentials** to git
2. **Don't hardcode API keys** in command-line args
3. **Don't share config files** with real credentials
4. **Don't use personal passwords** for SMTP (use app passwords)
5. **Don't commit `.env` files** with real values

---

## Usage Examples

### Using Default Configuration

```bash
# Will automatically load from:
# 1. .barque/email.yaml (if exists)
# 2. Environment variables
barque send report.md --to user@example.com
```

### Using Custom Config File

```bash
# Specify config file explicitly
barque send report.md \
  --to user@example.com \
  --email-config /path/to/custom-email.yaml
```

### Overriding with Environment Variables

```bash
# Override config file settings with env vars
RESEND_API_KEY="re_different_key" \
  barque send report.md --to user@example.com
```

### Overriding with Command-Line Args

```bash
# Highest priority - overrides everything
barque send report.md \
  --to user@example.com \
  --from reports@company.com \
  --provider smtp \
  --smtp-host smtp.gmail.com
```

---

## Configuration for Different Environments

### Development Setup

Create `.barque/email.yaml` for local development:

```yaml
provider: "resend"
resend:
  api_key: "re_test_xxxxxxxxxxxxx"  # Test API key

defaults:
  from_email: "dev@test.com"

# Development settings
development:
  dry_run: false
  test_mode: true
  test_email: "developer@test.com"
```

### Production Setup

Use environment variables in production (never config files with secrets):

```bash
# In production deployment (Kubernetes, Docker, etc.)
apiVersion: v1
kind: Secret
metadata:
  name: barque-email-config
type: Opaque
stringData:
  RESEND_API_KEY: "re_prod_xxxxxxxxxxxxx"
  POP_FROM: "reports@company.com"
```

### Staging Setup

Separate config for staging:

```bash
# Staging-specific environment
export RESEND_API_KEY="re_staging_xxxxxxxxxxxxx"
export POP_FROM="staging-reports@company.com"
```

---

## Configuration File Setup Script

Quick setup script to create your config:

```bash
#!/bin/bash
# setup-email-config.sh

# Create config directory
mkdir -p .barque

# Copy example config
cp .barque/email.example.yaml .barque/email.yaml

echo "✓ Created .barque/email.yaml"
echo ""
echo "Next steps:"
echo "1. Edit .barque/email.yaml with your credentials"
echo "2. Get Resend API key: https://resend.com/api-keys"
echo "3. Test with: barque send test_example.md --to your-email@example.com"
```

---

## Testing Your Configuration

### Test Configuration Loading

```bash
# Python interactive test
python3 << EOF
from barque.core.email_config import EmailConfigLoader

config = EmailConfigLoader.load()
print(f"Provider: {config.provider.value}")
print(f"From email: {config.defaults.from_email}")
print(f"Resend API key set: {bool(config.resend.api_key)}")
print(f"SMTP host: {config.smtp.host}")
EOF
```

### Test Email Sending

```bash
# Dry run test (see what would be sent)
barque send test_example.md \
  --to your-email@example.com \
  --dry-run

# Real test
barque send test_example.md \
  --to your-email@example.com
```

---

## Troubleshooting

### Config Not Loading

```bash
# Check which config file is being used
python3 -c "
from pathlib import Path
from barque.core.email_config import EmailConfigLoader

for path in EmailConfigLoader.CONFIG_SEARCH_PATHS:
    exists = '✓' if path.exists() else '✗'
    print(f'{exists} {path}')
"
```

### Environment Variables Not Working

```bash
# Verify env vars are set
echo "RESEND_API_KEY: ${RESEND_API_KEY:-(not set)}"
echo "POP_FROM: ${POP_FROM:-(not set)}"
echo "POP_SMTP_HOST: ${POP_SMTP_HOST:-(not set)}"
```

### Configuration Precedence Issues

```bash
# Test what final config looks like
python3 << EOF
from barque.core.email import EmailConfig

config = EmailConfig.from_file()
print(f"Provider: {config.provider}")
print(f"From: {config.from_email}")
print(f"Resend key: {config.resend_api_key[:10] if config.resend_api_key else 'Not set'}...")
EOF
```

---

## Integration with CI/CD

### GitHub Actions

```yaml
# .github/workflows/email-report.yml
name: Send Email Report

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM

jobs:
  send-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install BARQUE
        run: pip install -e .

      - name: Install Pop
        run: |
          brew install pop

      - name: Send Report
        env:
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
          POP_FROM: ${{ secrets.REPORT_FROM_EMAIL }}
        run: |
          barque send daily-report.md \
            --to team@company.com \
            --subject "Daily Report - $(date +%Y-%m-%d)"
```

### Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install -e .

# Install Pop
RUN apt-get update && \
    apt-get install -y curl && \
    curl -L https://github.com/charmbracelet/pop/releases/download/v0.1.0/pop_Linux_x86_64.tar.gz | tar -xz && \
    mv pop /usr/local/bin/

# Configuration from environment variables only
ENV RESEND_API_KEY=""
ENV POP_FROM=""

CMD ["barque", "--help"]
```

```bash
# Run with config
docker run \
  -e RESEND_API_KEY="re_xxxxxxxxxxxxx" \
  -e POP_FROM="reports@company.com" \
  -v $(pwd)/reports:/app/reports \
  barque:latest \
  send reports/daily.md --to team@company.com
```

---

## Advanced Configuration

### Multiple Profiles

```bash
# Different configs for different use cases
barque send report.md \
  --to client@example.com \
  --email-config .barque/email.client.yaml

barque send internal-report.md \
  --to team@company.com \
  --email-config .barque/email.internal.yaml
```

### Conditional Configuration

```bash
# Use different config based on environment
if [ "$ENVIRONMENT" = "production" ]; then
  CONFIG=".barque/email.prod.yaml"
else
  CONFIG=".barque/email.dev.yaml"
fi

barque send report.md --to user@example.com --email-config "$CONFIG"
```

---

## Migration from Old Setup

If you're upgrading from a previous version that used environment variables only:

```bash
# Old way (still works!)
export RESEND_API_KEY="re_xxxxxxxxxxxxx"
barque send report.md --to user@example.com

# New way (same result, more flexible)
# Create config file
cat > .barque/email.yaml << EOF
provider: "resend"
resend:
  api_key: "re_xxxxxxxxxxxxx"
EOF

barque send report.md --to user@example.com
```

**Both methods work!** The new config system is backward compatible.

---

## Summary

### For Quick Testing
- Use environment variables
- `export RESEND_API_KEY="..."`

### For Projects
- Create `.barque/email.yaml`
- Add to `.gitignore` (already done)
- Commit `.barque/email.example.yaml`

### For Production
- Use environment variables or secret management
- Never commit real credentials
- Use CI/CD secrets

---

**Configuration is secure, flexible, and production-ready!** 🔒

Questions? See [EMAIL-GUIDE.md](EMAIL-GUIDE.md) for usage examples.
