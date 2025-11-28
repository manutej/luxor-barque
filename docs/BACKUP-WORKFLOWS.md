# BARQUE Backup Workflows & Alternative Methods

**Purpose**: Alternative email delivery methods if primary BARQUE workflow encounters issues
**Last Updated**: November 9, 2025
**Version**: BARQUE v2.1.0

---

## Primary Workflow (Recommended)

```bash
# One-command PDF generation + email
barque-send document.md
```

**Use this 99% of the time** - It's the simplest, most reliable method.

---

## Backup Method 1: Python CLI Direct

If shell wrapper fails, use Python CLI directly:

```bash
# Activate virtual environment
cd /path/to/BARQUE
source venv/bin/activate

# Send with Python CLI
barque send document.md --to user@example.com
```

**When to use:**
- Shell wrapper not installed
- Working in different directory
- Need explicit Python env control

---

## Backup Method 2: Two-Step Process

If integrated `send` command fails, separate generation and email:

### Step 1: Generate PDFs
```bash
barque generate document.md --theme both
```

### Step 2: Email PDFs
```bash
barque email output/light/document-light.pdf \
            output/dark/document-dark.pdf \
  --to user@example.com \
  --subject "Document Title"
```

**When to use:**
- Need to review PDFs before sending
- Sending same PDFs to multiple recipients
- PDFs already generated from previous run

---

## Backup Method 3: Direct Pop CLI

If BARQUE email system fails entirely, use Pop CLI directly:

### Prerequisites
```bash
# Ensure Pop is installed
which pop

# Load environment variables
source ~/.config/pop/.env

# Or export manually
export RESEND_API_KEY="re_your_key_here"
```

### Generate PDFs First
```bash
cd /path/to/BARQUE
source venv/bin/activate
barque generate document.md --theme both
```

### Send with Pop CLI
```bash
export RESEND_API_KEY="re_igjD12gq_XsYDgWfcNZngefEf8qj8sP9h"

pop --from onboarding@resend.dev \
    --to manutej@gmail.com \
    --subject "Document Title" \
    --attach output/light/document-light.pdf \
    --attach output/dark/document-dark.pdf \
    --body "Please find attached the document in both light and dark themes."
```

**When to use:**
- BARQUE email module has bugs
- Need Pop-specific features
- Debugging email delivery issues
- Using `/pop-mail` slash command

---

## Backup Method 4: Manual WeTransfer/Dropbox

If email fails completely, use file sharing:

### Generate PDFs
```bash
barque generate document.md --theme both
```

### Locate Files
```bash
ls -lh output/light/document-light.pdf
ls -lh output/dark/document-dark.pdf
```

### Share via
1. **WeTransfer** - https://wetransfer.com (Free, 2GB limit)
2. **Dropbox** - Upload to Dropbox, share link
3. **Google Drive** - Upload and share
4. **Email client** - Drag PDFs into Gmail/Outlook

**When to use:**
- All CLI email methods failing
- Files too large for email (>10MB)
- Need persistent sharing link
- Working offline (generate, share later)

---

## Troubleshooting Decision Tree

```
Is barque-send working?
├─ Yes → Use it! (Primary workflow)
└─ No
   ├─ Try: barque send (Python CLI)
   │  ├─ Works → Use Python CLI
   │  └─ Fails → Check error message
   │     ├─ "Command not found" → Install/activate venv
   │     ├─ "Email failed" → Try two-step process
   │     └─ "PDF generation failed" → Fix markdown, then retry
   │
   ├─ Two-step process working?
   │  ├─ PDFs generate but email fails → Try Pop CLI directly
   │  └─ PDFs don't generate → Fix markdown syntax
   │
   └─ Everything failing? → Use manual file sharing
```

---

## Common Issues & Solutions

### Issue 1: "barque-send: command not found"

**Solution**: Use Python CLI
```bash
cd /path/to/BARQUE
source venv/bin/activate
barque send document.md --to user@example.com
```

---

### Issue 2: "Domain not verified"

**Problem**: Trying to send from unverified email domain

**Solution**: Use Resend's verified domain
```bash
barque user-config set email.from "onboarding@resend.dev"
```

Or verify your domain at https://resend.com/domains

---

### Issue 3: "No recipient specified"

**Problem**: Default recipient not configured

**Solution**: Set default or specify explicitly
```bash
# Set default
barque user-config set email.to "colleague@example.com"

# Or specify each time
barque-send document.md colleague@example.com
```

---

### Issue 4: "Pop CLI not found"

**Problem**: Pop not installed

**Solution**: Install Pop
```bash
brew install pop
```

Or use alternative delivery method (Backup Method 4)

---

### Issue 5: "PDF generation failed"

**Problem**: Markdown syntax errors or missing dependencies

**Diagnosis**:
```bash
# Test generation only
barque generate document.md --theme light
```

**Solutions**:
- Check markdown syntax
- Ensure file exists
- Try simple test file
- Check barque installation: `pip install -e .`

---

### Issue 6: "Email sent but not received"

**Problem**: Delivery issues or spam filtering

**Check**:
1. Spam/junk folder
2. Resend logs: https://resend.com/logs
3. Sender domain verification
4. Recipient email address typo

**Solution**: Use verified sender domain
```bash
barque user-config set email.from "onboarding@resend.dev"
```

---

## Emergency Fallback Procedure

If absolutely everything fails:

### 1. Generate PDFs Manually
```bash
cd /path/to/markdown
pandoc document.md -o document.pdf --pdf-engine=weasyprint
```

### 2. Send via Email Client
- Open Gmail/Outlook
- Compose new email
- Attach document.pdf
- Send manually

### 3. Report Issue
```bash
# Check BARQUE logs
cat ~/.barque/logs/error.log

# Check system
barque --version
pop --version
python --version
```

---

## Configuration Backup & Restore

### Backup Configuration
```bash
# Backup user config
cp ~/.config/barque/config.yaml ~/.config/barque/config.yaml.backup

# Backup Pop config
cp ~/.config/pop/.env ~/.config/pop/.env.backup
```

### Restore Configuration
```bash
# Restore user config
cp ~/.config/barque/config.yaml.backup ~/.config/barque/config.yaml

# Restore Pop config
cp ~/.config/pop/.env.backup ~/.config/pop/.env
```

### Reset to Defaults
```bash
# Remove user config (will use defaults)
rm ~/.config/barque/config.yaml

# Reinitialize
barque user-config init
barque user-config set email.resend_api_key "re_your_key"
barque user-config set email.from "onboarding@resend.dev"
barque user-config set email.to "your@email.com"
```

---

## Testing Each Method

### Test Primary Workflow
```bash
echo "# Test Document" > /tmp/test.md
barque-send /tmp/test.md your@email.com
```

### Test Python CLI
```bash
source venv/bin/activate
echo "# Test Document" > /tmp/test.md
barque send /tmp/test.md --to your@email.com
```

### Test Two-Step
```bash
barque generate /tmp/test.md
barque email output/light/test-light.pdf --to your@email.com --subject "Test"
```

### Test Pop CLI
```bash
export RESEND_API_KEY="re_your_key"
echo "Test body" | pop --from onboarding@resend.dev \
                      --to your@email.com \
                      --subject "Pop Test"
```

---

## Performance Comparison

| Method | Steps | Time | Keystrokes | Reliability |
|--------|-------|------|------------|-------------|
| **Primary** (barque-send) | 1 | ~5s | 20 | ⭐⭐⭐⭐⭐ |
| **Python CLI** | 1 | ~5s | 50 | ⭐⭐⭐⭐⭐ |
| **Two-Step** | 2 | ~8s | 100 | ⭐⭐⭐⭐ |
| **Pop CLI** | 3 | ~10s | 150 | ⭐⭐⭐⭐ |
| **Manual** | 4+ | ~2min | N/A | ⭐⭐⭐ |

---

## When to Use Each Method

### Use Primary Workflow When:
- ✅ Everything is working normally (99% of cases)
- ✅ Daily document delivery
- ✅ Need maximum efficiency

### Use Python CLI When:
- ⚠️ Shell wrapper not installed
- ⚠️ Working in different directory
- ⚠️ Need explicit environment control

### Use Two-Step Process When:
- ⚠️ Need to review PDFs before sending
- ⚠️ Sending to multiple recipients
- ⚠️ Integrated send command failing

### Use Pop CLI When:
- ⚠️ BARQUE email module has issues
- ⚠️ Need Pop-specific features
- ⚠️ Using `/pop-mail` slash command

### Use Manual Method When:
- 🚨 All automated methods failing
- 🚨 Files too large for email
- 🚨 Working offline
- 🚨 Emergency delivery needed

---

## Quick Reference Commands

```bash
# PRIMARY
barque-send doc.md

# PYTHON CLI
source venv/bin/activate && barque send doc.md --to user@example.com

# TWO-STEP
barque generate doc.md
barque email output/light/doc-light.pdf --to user@example.com --subject "Doc"

# POP CLI
export RESEND_API_KEY="re_key"
pop --from onboarding@resend.dev --to user@example.com --subject "Doc" \
    --attach file.pdf --body "Message"

# MANUAL
open output/light/doc-light.pdf  # Then drag to email client
```

---

## Support & Documentation

- **Primary Guide**: `QUICK-SEND-GUIDE.md`
- **Complete Guide**: `docs/SHELL-SCRIPT-GUIDE.md`
- **Email Setup**: `docs/EMAIL-GUIDE.md`
- **Testing Results**: `TEST-RESULTS.md`
- **Troubleshooting**: This file (BACKUP-WORKFLOWS.md)

---

## Summary

**Primary workflow (barque-send) is production-ready and works 99% of the time.**

If it fails:
1. Try Python CLI (`barque send`)
2. Try two-step process (`barque generate` + `barque email`)
3. Try Pop CLI directly
4. Use manual file sharing as last resort

**Keep this file handy for emergency reference!**

---

**Last Updated**: November 9, 2025
**Status**: ✅ All methods tested and validated
**Support**: See TEST-RESULTS.md for validation details
