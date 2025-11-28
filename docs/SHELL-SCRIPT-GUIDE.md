# BARQUE Shell Script Guide

**Simplified one-line email delivery for BARQUE**

## 🚀 Quick Start

```bash
# 1. Install the shell script
./scripts/install-shell-wrapper.sh

# 2. Set default recipient (optional but recommended)
barque user-config set email.to colleague@example.com

# 3. Send a PDF in one command!
barque-send report.md
```

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Shell Aliases](#shell-aliases)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

---

## Installation

### Option 1: Automatic Install (Recommended)

```bash
cd /path/to/BARQUE
./scripts/install-shell-wrapper.sh
```

This will:
- Copy `barque-send` to `/usr/local/bin/`
- Make it executable
- Add shell aliases to your `.zshrc` or `.bashrc`
- Verify installation

### Option 2: Manual Install

```bash
# Copy script
sudo cp scripts/barque-send /usr/local/bin/
sudo chmod +x /usr/local/bin/barque-send

# Add alias to your shell config
echo 'alias bsend="barque-send"' >> ~/.zshrc
source ~/.zshrc
```

### Verify Installation

```bash
which barque-send
# Output: /usr/local/bin/barque-send

barque-send --help
# Shows help message
```

---

## Configuration

### Set Default Recipient

For maximum convenience, set a default recipient:

```bash
barque user-config set email.to your-frequent-recipient@example.com
```

Now you can send files without specifying `--to` every time!

### Configuration Hierarchy

BARQUE uses this priority order for settings:

1. **Command-line arguments** (highest priority)
   ```bash
   barque-send report.md user@example.com --theme light
   ```

2. **Environment variables**
   ```bash
   export BARQUE_DEFAULT_TO="colleague@example.com"
   export BARQUE_THEME="both"
   barque-send report.md
   ```

3. **User config file** (`~/.config/barque/config.yaml`)
   ```yaml
   email:
     default_to_email: "colleague@example.com"
   preferences:
     default_theme: "both"
   ```

4. **Smart defaults** (lowest priority)

---

## Usage Examples

### Basic Usage

```bash
# Send to default recipient
barque-send report.md

# Send to specific recipient
barque-send report.md boss@company.com

# Send to multiple recipients
barque-send report.md --to ceo@company.com --to cfo@company.com
```

### Custom Themes

```bash
# Light theme only
barque-send report.md user@example.com --theme light

# Dark theme only
barque-send report.md user@example.com --theme dark

# Both themes (default)
barque-send report.md user@example.com --theme both
```

### Custom Subject Lines

```bash
barque-send quarterly-report.md \
  boss@company.com \
  --subject "Q4 2024 Financial Report"
```

### Quiet Mode

```bash
# Minimal output - only shows success/error
barque-send report.md --quiet
```

### Using Shell Aliases

After installation, use the short alias:

```bash
# Instead of: barque-send report.md
bsend report.md

# Send multiple files
bsend report1.md report2.md report3.md
```

---

## Shell Aliases

### Recommended Aliases

Add these to your `~/.zshrc` or `~/.bashrc`:

```bash
# Short alias for barque-send
alias bsend='barque-send'

# Send to your most common recipient
alias send-to-boss='barque-send --to boss@company.com'
alias send-to-team='barque-send --to team@company.com'

# Theme-specific sends
alias bsend-light='barque-send --theme light'
alias bsend-dark='barque-send --theme dark'

# Quick send to default with no output
alias qsend='barque-send --quiet'
```

### Project-Specific Aliases

For projects with specific recipients:

```bash
# In your project directory
cat >> .env << 'EOF'
export BARQUE_DEFAULT_TO="project-lead@company.com"
export BARQUE_THEME="both"
EOF

# Load in your shell session
source .env
```

---

## Advanced Usage

### Batch Processing with Shell Script

```bash
#!/bin/bash
# batch-send.sh - Send all reports to team

RECIPIENT="team@company.com"
THEME="both"

for report in reports/*.md; do
    echo "Sending: $report"
    barque-send "$report" "$RECIPIENT" --theme "$THEME" --quiet
    sleep 2  # Rate limiting
done

echo "✓ All reports sent!"
```

### Integration with Make

```makefile
# Makefile
.PHONY: send-report

send-report: report.md
	@barque-send report.md $(TO) --theme both
	@echo "Report sent to $(TO)"

# Usage: make send-report TO=boss@company.com
```

### CI/CD Integration

```yaml
# .github/workflows/send-report.yml
name: Generate and Send Report

on:
  schedule:
    - cron: '0 9 * * MON'  # Every Monday at 9am

jobs:
  send-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install BARQUE
        run: pip install -e .

      - name: Install Pop
        run: |
          wget https://github.com/charmbracelet/pop/releases/latest/download/pop_Linux_x86_64.tar.gz
          tar -xzf pop_Linux_x86_64.tar.gz
          sudo mv pop /usr/local/bin/

      - name: Configure BARQUE
        env:
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
        run: |
          barque user-config set email.resend_api_key "$RESEND_API_KEY"
          barque user-config set email.from "reports@company.com"

      - name: Send weekly report
        run: |
          barque-send reports/weekly.md \
            --to team@company.com \
            --subject "Weekly Report - $(date +%Y-%m-%d)"
```

---

## Environment Variables

### Available Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BARQUE_DEFAULT_TO` | Default recipient email | `colleague@example.com` |
| `BARQUE_THEME` | Default PDF theme | `both`, `light`, `dark` |
| `RESEND_API_KEY` | Resend API key | `re_abc123...` |
| `BARQUE_FROM_EMAIL` | Default sender email | `you@example.com` |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USERNAME` | SMTP username | `your@email.com` |
| `SMTP_PASSWORD` | SMTP password | `app-password` |

### Using .env Files

```bash
# Create .env file
cat > .env << 'EOF'
export BARQUE_DEFAULT_TO="colleague@example.com"
export BARQUE_THEME="both"
export RESEND_API_KEY="re_your_key_here"
EOF

# Load into shell
source .env

# Now use simplified commands
barque-send report.md  # Uses settings from .env
```

---

## Troubleshooting

### "barque-send: command not found"

**Solution 1:** Install the wrapper script
```bash
./scripts/install-shell-wrapper.sh
```

**Solution 2:** Add to PATH
```bash
export PATH="/path/to/BARQUE/scripts:$PATH"
echo 'export PATH="/path/to/BARQUE/scripts:$PATH"' >> ~/.zshrc
```

### "No recipient specified and no default configured"

**Solution:** Set a default recipient
```bash
barque user-config set email.to your-colleague@example.com
```

Or specify recipient explicitly:
```bash
barque-send report.md user@example.com
```

### "Pop CLI not found"

**Solution:** Install Charm Pop
```bash
# macOS
brew install pop

# Linux
wget https://github.com/charmbracelet/pop/releases/latest/download/pop_Linux_x86_64.tar.gz
tar -xzf pop_Linux_x86_64.tar.gz
sudo mv pop /usr/local/bin/

# Go
go install github.com/charmbracelet/pop@latest
```

### "Email sent successfully but recipient didn't receive it"

**Check:**
1. Spam/junk folder
2. Resend API key is valid: `barque user-config get email.resend_api_key`
3. Sender email is verified in Resend dashboard
4. Check Resend logs: https://resend.com/logs

### PDF Generation Fails

**Solution:** Check markdown file
```bash
# Test PDF generation only
barque generate report.md --theme both

# Check output
ls -la output/light/
ls -la output/dark/
```

---

## Performance Tips

### 1. Pre-configure User Settings

Set up once, use forever:
```bash
barque user-config set email.resend_api_key "re_your_key"
barque user-config set email.from "you@example.com"
barque user-config set email.to "colleague@example.com"
barque user-config set preferences.theme "both"
```

Now just: `barque-send report.md`

### 2. Use Aliases for Common Tasks

```bash
alias daily-report='barque-send ~/reports/daily.md boss@company.com'
alias weekly-report='barque-send ~/reports/weekly.md team@company.com --theme both'
```

### 3. Batch Processing with Rate Limiting

```bash
for file in *.md; do
  barque-send "$file" --quiet
  sleep 2  # Respect API rate limits
done
```

---

## Examples by Use Case

### Daily Standup Reports

```bash
# Alias in ~/.zshrc
alias standup='barque-send ~/notes/standup-$(date +%Y-%m-%d).md team@company.com --subject "Daily Standup - $(date +%b %d)"'

# Usage
standup
```

### Client Deliverables

```bash
# With custom branding
barque-send client-proposal.md \
  client@example.com \
  --theme both \
  --subject "Proposal: Q1 2024 Strategy" \
  --body "Dear Client,

Please find attached our proposal for Q1 2024.

Best regards,
Your Team"
```

### Team Documentation

```bash
# Send documentation to whole team
barque-send architecture-guide.md \
  --to dev-team@company.com \
  --to product@company.com \
  --to design@company.com \
  --subject "Updated Architecture Guide"
```

---

## Best Practices

### ✅ Do's

1. **Set default recipient** for frequent sends
2. **Use aliases** for repetitive tasks
3. **Pre-configure API keys** in user config (not in scripts)
4. **Use `--quiet`** in automated scripts
5. **Add rate limiting** when sending multiple emails

### ❌ Don'ts

1. **Don't hardcode API keys** in shell scripts
2. **Don't spam** - respect rate limits
3. **Don't skip recipient validation** - always verify before bulk sends
4. **Don't ignore errors** - check exit codes in scripts

---

## Shell Script Template

Save this as `send-template.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Configuration
RECIPIENT="${1:-}"
FILE="${2:-}"

if [ -z "$RECIPIENT" ] || [ -z "$FILE" ]; then
    echo "Usage: $0 <recipient@email.com> <file.md>"
    exit 1
fi

# Send with BARQUE
barque-send "$FILE" "$RECIPIENT" \
    --theme both \
    --quiet

if [ $? -eq 0 ]; then
    echo "✓ Sent $FILE to $RECIPIENT"
else
    echo "✗ Failed to send $FILE"
    exit 1
fi
```

Usage:
```bash
chmod +x send-template.sh
./send-template.sh boss@company.com report.md
```

---

## Summary

The BARQUE shell script wrapper provides:

✅ **One-line sends** - `barque-send report.md`
✅ **Smart defaults** - Pre-configure recipients and themes
✅ **Shell aliases** - `bsend` instead of `barque-send`
✅ **Scriptable** - Use in automation and CI/CD
✅ **Error handling** - Graceful failures with helpful messages

**Next Steps:**
1. Run `./scripts/install-shell-wrapper.sh`
2. Set default recipient: `barque user-config set email.to colleague@example.com`
3. Send your first email: `barque-send report.md`

---

**Questions?** Check [EMAIL-GUIDE.md](EMAIL-GUIDE.md) for detailed email configuration.
