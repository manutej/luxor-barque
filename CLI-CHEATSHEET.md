# BARQUE CLI Cheat Sheet

Quick reference for BARQUE commands.

---

## Setup (One-Time)

```bash
# Install BARQUE
pip install barque

# Set up email (optional)
export RESEND_API_KEY="re_your_key"  # Get from resend.com

# Initialize in project
barque init
```

---

## PDF Generation

### Single File
```bash
barque generate document.md              # Both themes
barque generate document.md --theme light # Light only
barque generate document.md --theme dark  # Dark only
barque generate doc.md --output pdfs/     # Custom output
```

### Batch Processing
```bash
barque batch docs/                       # All .md files
barque batch docs/ --theme light         # Light theme only
barque batch docs/ --workers 8           # Parallel (8 workers)
barque batch docs/ --recursive           # Include subdirs
```

---

## Email Delivery

### Generate and Send
```bash
# Prerequisites: export RESEND_API_KEY="re_..."

barque send report.md --to user@example.com
barque send doc.md --to alice@co.com --to bob@co.com
barque send file.md --to boss@co.com --theme light
barque send report.md --to team@co.com --subject "Q4 Results"
```

### Send Existing Files
```bash
barque email report.pdf --to user@example.com --subject "Report"
barque email doc.pdf --to team@co.com --cc boss@co.com
barque email file1.pdf file2.pdf --to client@example.com --subject "Files"
```

---

## Configuration

```bash
barque config --show        # View current config
barque config --validate    # Check config syntax
barque config --reset       # Reset to defaults
```

---

## Cleanup

```bash
barque clean               # Clean output directory
barque clean --all         # Clean output + cache
```

---

## Common Workflows

### Daily Report
```bash
#!/bin/bash
barque send daily-report.md \
  --to team@company.com \
  --subject "Daily Report - $(date +%Y-%m-%d)"
```

### Batch + Email
```bash
# Generate all reports
barque batch reports/ --theme light

# Email each one
for pdf in output/light/*.pdf; do
  barque email "$pdf" --to client@example.com --subject "$(basename $pdf)"
done
```

### Multiple Recipients
```bash
barque send summary.md \
  --to alice@co.com \
  --to bob@co.com \
  --to charlie@co.com \
  --cc manager@co.com \
  --subject "Weekly Summary"
```

---

## Environment Variables

```bash
# Email - Resend (recommended)
export RESEND_API_KEY="re_your_key"

# Email - SMTP (alternative)
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="user@gmail.com"
export SMTP_PASSWORD="app-password"

# Defaults
export DEFAULT_FROM_EMAIL="noreply@myapp.com"
```

---

## File Locations

| Path | Purpose |
|------|---------|
| `.barque/config.yaml` | Main configuration |
| `.barque/email.yaml` | Email settings (optional) |
| `.barque/themes/` | Custom themes |
| `output/` | Generated PDFs |
| `.env` | Environment variables (not committed) |

---

## Quick Troubleshooting

**PDFs not generating?**
```bash
which pandoc  # Check pandoc installed
brew install pandoc  # macOS
```

**Email not working?**
```bash
echo $RESEND_API_KEY  # Check API key set
pop --version         # Check Pop installed
```

**Command not found?**
```bash
pip install barque    # Install BARQUE
source ~/.zshrc       # Reload shell
```

---

## Examples by Use Case

### Academic Paper
```bash
barque generate paper.md --theme both
```

### Client Report
```bash
barque send client-report.md \
  --to client@example.com \
  --theme light \
  --subject "Monthly Analytics Report"
```

### Team Documentation
```bash
barque batch docs/ --output team-pdfs/ --workers 4
```

### Automated Reports
```bash
# cron: 0 9 * * * /path/to/script.sh
barque send daily-metrics.md --to team@company.com
```

---

## Options Reference

### Common Options
- `--theme` - `light`, `dark`, `both`
- `--output` - Output directory path
- `--config` - Custom config file

### Email Options
- `--to` - Recipient (repeatable)
- `--from` - Sender email
- `--subject` - Email subject
- `--cc` - CC recipient (repeatable)
- `--bcc` - BCC recipient (repeatable)
- `--body` - Email body text
- `--provider` - `resend` or `smtp`
- `--email-config` - Email config file

### Batch Options
- `--workers` - Parallel workers (default: 4)
- `--recursive` - Process subdirectories

---

## Documentation

📖 [README.md](README.md) - Overview and features
📖 [EMAIL-SETUP.md](EMAIL-SETUP.md) - 5-minute email setup
📖 [EMAIL-GUIDE.md](EMAIL-GUIDE.md) - Complete email docs
📖 [CONFIGURATION-GUIDE.md](CONFIGURATION-GUIDE.md) - Advanced config

---

**Quick Start**: `barque generate document.md` → PDF in `output/`
**With Email**: `export RESEND_API_KEY="..."` → `barque send doc.md --to you@example.com`
