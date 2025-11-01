# BARQUE Email Quick Start

**Get started with email delivery in 5 minutes**

## Prerequisites

1. **Install Charm Pop**

```bash
brew install pop
```

2. **Get Resend API Key** (recommended)

Sign up at https://resend.com and get your API key from https://resend.com/api-keys

3. **Set Environment Variable**

```bash
export RESEND_API_KEY="re_xxxxxxxxxxxxx"

# Add to ~/.zshrc or ~/.bashrc for persistence
echo 'export RESEND_API_KEY="re_xxxxxxxxxxxxx"' >> ~/.zshrc
```

## Usage Examples

### 1. Generate PDF and Send

```bash
barque send report.md --to boss@company.com
```

That's it! BARQUE will:
1. Generate PDF in both themes
2. Send via email with auto-generated subject
3. Include professional email body

### 2. Send with Custom Subject

```bash
barque send quarterly-report.md \
  --to team@company.com \
  --subject "Q4 Performance Report"
```

### 3. Send to Multiple Recipients

```bash
barque send analysis.md \
  --to john@company.com \
  --to jane@company.com \
  --to management@company.com
```

### 4. Send Existing PDF

```bash
barque email report-light.pdf \
  --to client@example.com \
  --subject "Analysis Results"
```

### 5. Send with Custom Body

```bash
barque send report.md \
  --to client@example.com \
  --subject "Monthly Analysis" \
  --body "# Monthly Report

Dear Client,

Please find attached the monthly analysis report.

Key highlights:
- Revenue increased 15%
- Customer satisfaction: 92%

Best regards,
Your Team"
```

## Alternative: Using SMTP (Gmail Example)

If you prefer SMTP over Resend:

```bash
# Set SMTP environment variables
export POP_SMTP_HOST="smtp.gmail.com"
export POP_SMTP_PORT="587"
export POP_SMTP_USERNAME="your-email@gmail.com"
export POP_SMTP_PASSWORD="your-app-password"

# Send using SMTP
barque send report.md \
  --to recipient@example.com \
  --provider smtp
```

**Note**: For Gmail, you'll need an [App Password](https://support.google.com/accounts/answer/185833).

## Common Workflows

### Daily Report Automation

```bash
#!/bin/bash
# daily-report.sh

barque send daily-summary.md \
  --to management@company.com \
  --subject "Daily Report - $(date +%Y-%m-%d)"
```

Schedule with cron:
```bash
crontab -e
# Add: 0 9 * * * /path/to/daily-report.sh
```

### Send Light Theme for Printing

```bash
barque send document.md \
  --to print@office.com \
  --theme light \
  --subject "Document for Printing"
```

### Batch Process and Email

```bash
# Generate all reports
barque batch reports/

# Email each report
for pdf in output/light/*.pdf; do
  barque email "$pdf" \
    --to stakeholders@company.com \
    --subject "Report: $(basename $pdf .pdf)"
done
```

## Troubleshooting

### Pop Not Found

```bash
# Install Pop
brew install pop

# Verify installation
pop --version
```

### Email Not Sending

Check your API key:
```bash
echo $RESEND_API_KEY  # Should show your key
```

If empty, set it:
```bash
export RESEND_API_KEY="re_xxxxxxxxxxxxx"
```

### Permission Denied

Make sure Pop has necessary permissions. On macOS, check Security & Privacy settings.

## Next Steps

- Read the full [EMAIL-GUIDE.md](EMAIL-GUIDE.md) for advanced usage
- Configure custom email templates
- Set up microservice integration
- Explore batch processing workflows

## Support

- BARQUE Documentation: See [README.md](README.md)
- Pop Documentation: https://github.com/charmbracelet/pop
- Resend Documentation: https://resend.com/docs

---

**Ready to revolutionize your document workflows!** 🚀
