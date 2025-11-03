# BARQUE Email Setup Guide

Quick 5-minute setup for sending PDFs via email.

---

## Prerequisites

- Resend account (recommended) OR SMTP server credentials
- Charm Pop CLI installed (automatic on first use)

---

## Option 1: Resend (Recommended)

Resend is the easiest and fastest email provider to set up.

### Step 1: Get Resend API Key

1. Sign up at [resend.com](https://resend.com)
2. Create API key in dashboard
3. Copy the API key (starts with `re_...`)

### Step 2: Set Environment Variable

**macOS/Linux:**
```bash
# Add to ~/.zshrc or ~/.bashrc
export RESEND_API_KEY="re_your_api_key_here"

# Reload shell
source ~/.zshrc  # or ~/.bashrc
```

**Verify:**
```bash
echo $RESEND_API_KEY
```

### Step 3: Test Email Delivery

```bash
# Generate and send a test PDF
barque send README.md \
  --to your-email@example.com \
  --from noreply@your-domain.com \
  --subject "Test PDF from BARQUE"
```

✅ **Done!** Check your email inbox.

---

## Option 2: SMTP

For Gmail, Outlook, or custom SMTP servers.

### Step 1: Get SMTP Credentials

**Gmail:**
- Enable 2FA in Google Account
- Generate App Password: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
- Use App Password (NOT your Gmail password)

**Outlook:**
- Use account email and password
- May need to enable "Less secure apps"

### Step 2: Set Environment Variables

```bash
# Add to ~/.zshrc or ~/.bashrc
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"

# Reload shell
source ~/.zshrc
```

### Step 3: Test SMTP Email

```bash
barque send README.md \
  --to recipient@example.com \
  --from your-email@gmail.com \
  --subject "Test via SMTP" \
  --provider smtp
```

---

## Quick Reference

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `RESEND_API_KEY` | For Resend | Resend API key | `re_abc123...` |
| `SMTP_HOST` | For SMTP | SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | For SMTP | SMTP port | `587` |
| `SMTP_USERNAME` | For SMTP | Email address | `user@gmail.com` |
| `SMTP_PASSWORD` | For SMTP | Password/App Password | `****` |

### Commands

**Generate and send:**
```bash
barque send document.md --to user@example.com
```

**Send existing PDF:**
```bash
barque email report.pdf --to user@example.com --subject "Monthly Report"
```

**Multiple recipients:**
```bash
barque send doc.md \
  --to user1@example.com \
  --to user2@example.com \
  --cc manager@example.com
```

**Custom theme:**
```bash
barque send report.md --to boss@company.com --theme light
```

---

## Verification Checklist

✅ **API key or SMTP credentials configured**
```bash
# Check Resend
echo $RESEND_API_KEY

# Check SMTP
echo $SMTP_HOST
echo $SMTP_USERNAME
```

✅ **Charm Pop installed**
```bash
pop --version
```

✅ **BARQUE working**
```bash
barque --version
```

✅ **Test email sent successfully**
```bash
barque send README.md --to your-email@example.com
```

---

## Security Best Practices

### ✅ DO:
- Use environment variables for credentials
- Use Resend API keys (more secure than SMTP)
- Use App Passwords for Gmail (NOT main password)
- Rotate API keys regularly
- Verify sender domains in Resend

### ❌ DON'T:
- Hardcode API keys in scripts
- Commit `.env` files to git
- Share API keys in chat/email
- Use main Gmail password
- Expose credentials in logs

---

## Troubleshooting

### "pop: command not found"

Charm Pop will auto-install on first email command. Or manually:

**macOS:**
```bash
brew install charmbracelet/tap/pop
```

**Linux:**
```bash
# Download from releases
wget https://github.com/charmbracelet/pop/releases/latest/download/pop_linux_amd64.tar.gz
tar -xzf pop_linux_amd64.tar.gz
sudo mv pop /usr/local/bin/
```

### "Authentication failed"

**Resend:**
- Check API key is correct: `echo $RESEND_API_KEY`
- Verify API key is active in Resend dashboard
- Ensure sender domain is verified in Resend

**SMTP:**
- Gmail: Use App Password, NOT regular password
- Check credentials: `echo $SMTP_USERNAME`
- Verify port: 587 for TLS, 465 for SSL

### "Sender domain not verified"

**Resend:**
- Add and verify your domain in Resend dashboard
- Use verified domain in `--from` address
- Or use `onboarding@resend.dev` for testing

### Environment variables not loaded

```bash
# Reload shell configuration
source ~/.zshrc  # or ~/.bashrc

# Verify
env | grep RESEND
env | grep SMTP
```

---

## Advanced Configuration

### Config File Method

Create `.barque/email.yaml`:

```yaml
provider: "resend"

resend:
  api_key: ""  # Set via RESEND_API_KEY env var

defaults:
  from_email: "reports@your-domain.com"
  subject_prefix: "[BARQUE]"

smtp:
  host: "smtp.gmail.com"
  port: 587
  username: ""  # Set via SMTP_USERNAME env var
  password: ""  # Set via SMTP_PASSWORD env var
  use_tls: true
```

Use config:
```bash
barque send doc.md --to user@example.com --email-config .barque/email.yaml
```

### Environment-Specific Configs

**Development:**
```bash
# .env.development
RESEND_API_KEY=re_test_key
```

**Production:**
```bash
# .env.production
RESEND_API_KEY=re_prod_key
```

Load environment:
```bash
source .env.development
barque send doc.md --to dev@example.com
```

---

## Examples

### Example 1: Daily Report

```bash
#!/bin/bash
# daily-report.sh

# Generate today's report
barque generate daily-report.md --theme both

# Send to team
barque email output/both/daily-report.pdf \
  --to team@company.com \
  --cc manager@company.com \
  --subject "Daily Report - $(date +%Y-%m-%d)" \
  --body "Attached is today's automated report."
```

### Example 2: Batch Reports

```bash
#!/bin/bash
# batch-reports.sh

# Generate all reports
barque batch reports/ --theme light

# Send each report
for pdf in output/light/*.pdf; do
  barque email "$pdf" \
    --to client@example.com \
    --subject "Report: $(basename $pdf .pdf)"
done
```

### Example 3: Weekly Summary

```bash
#!/bin/bash
# weekly-summary.sh

RECIPIENTS=(
  "alice@company.com"
  "bob@company.com"
  "charlie@company.com"
)

# Generate summary
barque send weekly-summary.md \
  --theme both \
  --subject "Weekly Summary - Week $(date +%V)" \
  $(printf -- '--to %s ' "${RECIPIENTS[@]}")
```

---

## Next Steps

1. ✅ Set up environment variables
2. ✅ Test email delivery
3. ✅ Automate with scripts
4. 📖 Read [EMAIL-GUIDE.md](EMAIL-GUIDE.md) for advanced features
5. 🚀 Integrate with LUMOS/LUMINA microservices

---

## Support

Having issues? Check:
- [EMAIL-GUIDE.md](EMAIL-GUIDE.md) - Complete email documentation
- [CONFIGURATION-GUIDE.md](CONFIGURATION-GUIDE.md) - Advanced config
- [Charm Pop Docs](https://github.com/charmbracelet/pop)
- [Resend Docs](https://resend.com/docs)

---

**Quick Start**: Set `RESEND_API_KEY` and run `barque send doc.md --to you@example.com`
