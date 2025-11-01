# BARQUE Email Guide

**Email delivery extension for BARQUE using Charm Pop**

## Overview

BARQUE now includes powerful email delivery capabilities powered by [Charm Pop](https://github.com/charmbracelet/pop), allowing you to:

- Send generated PDFs directly via email
- Email any files from the command line
- Support multiple recipients (to, cc, bcc)
- Use Resend API or SMTP for delivery
- Customize email body with markdown

## Installation

### Install Charm Pop

First, install the Charm Pop CLI:

```bash
# macOS/Linux (Homebrew)
brew install pop

# Go
go install github.com/charmbracelet/pop@latest
```

### Verify Installation

```bash
pop --version
```

## Configuration

### Option 1: Resend API (Recommended)

1. Sign up for Resend at https://resend.com
2. Get your API key from https://resend.com/api-keys
3. Set environment variable:

```bash
export RESEND_API_KEY="re_xxxxxxxxxxxxx"
```

### Option 2: SMTP

Configure SMTP via environment variables:

```bash
export POP_SMTP_HOST="smtp.gmail.com"
export POP_SMTP_PORT="587"
export POP_SMTP_USERNAME="your-email@gmail.com"
export POP_SMTP_PASSWORD="your-app-password"
```

For Gmail, you'll need to create an [App Password](https://support.google.com/accounts/answer/185833).

### Optional: Default Sender

```bash
export POP_FROM="your-name@example.com"
export POP_SIGNATURE="
Best regards,
Your Name
"
```

## Commands

BARQUE provides two email commands:

### 1. `barque send` - Generate and Send

Generate PDF from markdown and send it via email in one command:

```bash
barque send document.md \
  --to recipient@example.com \
  --subject "Quarterly Report"
```

**Options:**
- `--to` - Recipient email (required, can specify multiple times)
- `--subject` - Email subject (optional, auto-generated if not provided)
- `--from` - Sender email address
- `--theme` - PDF theme: light, dark, or both (default: both)
- `--output` - Output directory for PDFs
- `--provider` - Email provider: resend or smtp (default: resend)
- `--body` - Custom email body text

### 2. `barque email` - Send Existing Files

Send any existing files via email:

```bash
barque email report.pdf invoice.pdf \
  --to client@example.com \
  --subject "Monthly Reports" \
  --body "Please find attached reports for review."
```

**Options:**
- Files to send (required, can specify multiple)
- `--to` - Recipient email (required, can specify multiple times)
- `--subject` - Email subject (required)
- `--from` - Sender email address
- `--body` - Custom email body text
- `--cc` - CC recipient (can specify multiple times)
- `--bcc` - BCC recipient (can specify multiple times)
- `--provider` - Email provider: resend or smtp
- `--smtp-host`, `--smtp-port`, `--smtp-username`, `--smtp-password` - SMTP configuration

## Usage Examples

### Basic: Generate and Send PDF

```bash
barque send report.md --to boss@company.com
```

### Multiple Recipients

```bash
barque send report.md \
  --to john@example.com \
  --to jane@example.com \
  --to team@example.com
```

### With CC and BCC

```bash
barque email report.pdf \
  --to client@example.com \
  --cc manager@company.com \
  --bcc archive@company.com \
  --subject "Project Update"
```

### Custom Email Body

```bash
barque send report.md \
  --to client@example.com \
  --subject "Q4 Analysis" \
  --body "# Q4 Performance Report

Dear Client,

Please review the attached Q4 performance analysis.

Key highlights:
- Revenue increased 25%
- Customer satisfaction: 95%
- New product launches: 3

Best regards,
Your Team"
```

### Light Theme Only

```bash
barque send document.md \
  --to print@office.com \
  --theme light \
  --subject "Document for Printing"
```

### Using SMTP

```bash
barque send report.md \
  --to user@example.com \
  --provider smtp \
  --smtp-host smtp.gmail.com \
  --smtp-port 587 \
  --smtp-username your-email@gmail.com \
  --smtp-password your-app-password
```

### Send Multiple Existing Files

```bash
barque email \
  report-light.pdf \
  report-dark.pdf \
  summary.pdf \
  --to team@company.com \
  --subject "Complete Report Package"
```

## Environment Variables

You can configure defaults via environment variables to avoid repeating options:

```bash
# Email provider
export RESEND_API_KEY="re_xxxxxxxxxxxxx"

# SMTP (alternative to Resend)
export POP_SMTP_HOST="smtp.gmail.com"
export POP_SMTP_PORT="587"
export POP_SMTP_USERNAME="your-email@gmail.com"
export POP_SMTP_PASSWORD="your-app-password"

# Sender defaults
export POP_FROM="reports@company.com"
export POP_SIGNATURE="
---
Automated Report System
BARQUE v2.0.0
"
```

Add these to your `~/.zshrc` or `~/.bashrc` for persistence.

## Workflow Integration

### Automated Daily Reports

```bash
#!/bin/bash
# daily-report.sh

# Generate and send daily report
barque send daily-summary.md \
  --to management@company.com \
  --cc operations@company.com \
  --subject "Daily Report - $(date +%Y-%m-%d)"
```

### Batch Generate and Send

```bash
# Generate all reports first
barque batch reports/ --output /tmp/batch-reports

# Send each report
for pdf in /tmp/batch-reports/light/*.pdf; do
  barque email "$pdf" \
    --to stakeholders@company.com \
    --subject "Report: $(basename $pdf .pdf)"
done
```

### Integration with Scripts

```python
import subprocess
import sys

def send_report(markdown_file, recipient, subject=None):
    """Generate PDF and send via email"""
    cmd = [
        'barque', 'send', markdown_file,
        '--to', recipient
    ]

    if subject:
        cmd.extend(['--subject', subject])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✓ Report sent to {recipient}")
    else:
        print(f"✗ Failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

# Usage
send_report('monthly-metrics.md', 'ceo@company.com', 'Monthly Metrics Report')
```

## Microservice Architecture

BARQUE's email functionality is designed to be easily packaged as a microservice:

```python
# barque_service.py
from flask import Flask, request, jsonify
import subprocess
import tempfile
from pathlib import Path

app = Flask(__name__)

@app.route('/generate-and-send', methods=['POST'])
def generate_and_send():
    """
    API endpoint to generate PDF and send via email

    POST /generate-and-send
    {
      "markdown": "# Report content...",
      "to": ["recipient@example.com"],
      "subject": "Report",
      "theme": "both"
    }
    """
    data = request.json

    # Save markdown to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(data['markdown'])
        temp_file = f.name

    try:
        # Build barque command
        cmd = [
            'barque', 'send', temp_file,
            '--subject', data['subject'],
            '--theme', data.get('theme', 'both')
        ]

        for recipient in data['to']:
            cmd.extend(['--to', recipient])

        # Execute
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Report sent'})
        else:
            return jsonify({'success': False, 'error': result.stderr}), 500

    finally:
        Path(temp_file).unlink()

if __name__ == '__main__':
    app.run(port=5000)
```

## Error Handling

### Pop Not Installed

```
✗ Charm Pop is not installed!

Charm Pop is not installed. Install it with:

macOS/Linux:
  brew install pop

Go:
  go install github.com/charmbracelet/pop@latest
```

**Solution**: Install Pop using one of the methods shown.

### API Key Missing

```
✗ Failed to send email
   Error: RESEND_API_KEY environment variable not set
```

**Solution**: Set your Resend API key:
```bash
export RESEND_API_KEY="re_xxxxxxxxxxxxx"
```

### SMTP Authentication Failed

```
✗ Failed to send email
   Error: 535 Authentication failed
```

**Solution**:
- Verify SMTP credentials
- For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)
- Check SMTP host and port

## Tips and Best Practices

### 1. Use Environment Variables

Store credentials in environment variables rather than command-line arguments:

```bash
# Add to ~/.zshrc or ~/.bashrc
export RESEND_API_KEY="re_xxxxxxxxxxxxx"
export POP_FROM="reports@company.com"
```

### 2. Test Email Delivery

Test with a small file first:

```bash
echo "# Test" > test.md
barque send test.md --to your-email@example.com --subject "Test"
```

### 3. Markdown Email Bodies

The `--body` option supports markdown formatting:

```bash
barque email report.pdf \
  --to client@example.com \
  --subject "Report" \
  --body "# Executive Summary

**Key Findings:**
- Revenue: $1.2M
- Growth: 25%

See attached for details."
```

### 4. Automation with Cron

Schedule daily reports:

```bash
# crontab -e
0 9 * * * /path/to/barque send /path/to/daily-report.md --to team@company.com
```

### 5. Integration with LUMOS/LUMINA

BARQUE's microservice architecture makes it easy to integrate with other systems:

```bash
# POST to BARQUE microservice from LUMOS
curl -X POST http://barque-service:5000/generate-and-send \
  -H "Content-Type: application/json" \
  -d '{
    "markdown": "# Performance Report...",
    "to": ["analyst@company.com"],
    "subject": "AI-Generated Analysis"
  }'
```

## Future Enhancements

Planned features for the email extension:

- [ ] Email templates with placeholders
- [ ] Attachment size warnings
- [ ] Delivery status tracking
- [ ] Retry logic with exponential backoff
- [ ] Bulk email with rate limiting
- [ ] HTML email body rendering
- [ ] Email scheduling
- [ ] Delivery receipts
- [ ] Integration with email tracking services

## Support

For issues or questions:

- BARQUE Issues: Create issue in project repository
- Pop Issues: https://github.com/charmbracelet/pop/issues
- Resend Support: https://resend.com/docs

---

**BARQUE v2.0.0** - Reinventing knowledge work with beautiful documents and seamless delivery
