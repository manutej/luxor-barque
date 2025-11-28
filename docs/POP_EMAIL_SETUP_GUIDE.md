# Pop Email Setup Guide

**Send emails from your terminal using Charm Pop CLI with Gmail SMTP**

This guide will help you set up Pop to send emails from your Gmail account to any recipient.

---

## 📦 What is Pop?

[Pop](https://github.com/charmbracelet/pop) is a command-line tool by Charm that sends emails. It supports both API-based services (like Resend) and SMTP servers (like Gmail).

**Benefits:**
- ✅ Send emails directly from terminal
- ✅ Attach files easily
- ✅ Works with Gmail, SendGrid, Mailgun, SMTP servers
- ✅ Simple, clean interface

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Pop

**macOS/Linux (Homebrew):**
```bash
brew install pop
```

**Other platforms:** See [Pop installation docs](https://github.com/charmbracelet/pop#installation)

**Verify installation:**
```bash
pop --version
```

---

### Step 2: Get Gmail App Password

You need a Gmail App Password (not your regular Gmail password).

1. **Enable 2-Factor Authentication** on your Google account (required):
   - Visit: https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Generate App Password**:
   - Visit: https://myaccount.google.com/apppasswords
   - Sign in to your Google account
   - App name: "Pop CLI" (or any name you like)
   - Click "Create"
   - Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
   - ⚠️ **Save it now** - you can't view it again!

📚 **Help:** [Google's App Password Guide](https://support.google.com/accounts/answer/185833)

---

### Step 3: Configure Pop

Create a configuration directory and environment file:

```bash
# Create config directory
mkdir -p ~/.config/pop

# Create environment file
cat > ~/.config/pop/.env << 'EOF'
# Pop Email Configuration
# Gmail SMTP Setup

export POP_SMTP_HOST=smtp.gmail.com
export POP_SMTP_PORT=587
export POP_SMTP_USERNAME=your-email@gmail.com
export POP_SMTP_PASSWORD="your 16 char app password"
export POP_FROM=your-email@gmail.com
EOF

# Secure the file (important!)
chmod 600 ~/.config/pop/.env
```

**⚠️ Important:** Replace:
- `your-email@gmail.com` with your actual Gmail address
- `your 16 char app password` with the password from Step 2

---

## ✅ Test Your Setup

### Load configuration and send test email:

```bash
# Load environment variables
source ~/.config/pop/.env

# Send test email to yourself
pop --to your-email@gmail.com \
  --subject "Pop Test Email" \
  --body "Success! Pop is working with Gmail SMTP."
```

**Check your inbox!** You should receive the test email within seconds.

---

## 📧 How to Use Pop

### Basic Email
```bash
source ~/.config/pop/.env
pop --to recipient@example.com \
  --subject "Hello" \
  --body "Your message here"
```

### With Attachments
```bash
source ~/.config/pop/.env
pop --to recipient@example.com \
  --subject "Documents" \
  --body "Please find attached files" \
  --attach file1.pdf \
  --attach file2.pdf
```

### Multiple Recipients
```bash
# Send to multiple people (loop)
for recipient in alice@example.com bob@example.com; do
  pop --to $recipient --subject "Hello" --body "Message"
done
```

---

## 🔧 Helper Script (Optional)

Create a convenience script for easier email sending:

```bash
cat > ~/.config/pop/send-email.sh << 'EOF'
#!/bin/bash
# Pop email helper script

# Load environment
source ~/.config/pop/.env

# Usage: send-email.sh recipient@example.com "Subject" "Body" [file1.pdf file2.pdf...]
TO="$1"
SUBJECT="$2"
BODY="$3"
shift 3

# Build command
CMD="pop --to \"$TO\" --subject \"$SUBJECT\" --body \"$BODY\""

# Add attachments
for file in "$@"; do
  CMD="$CMD --attach \"$file\""
done

# Execute
eval $CMD
EOF

chmod +x ~/.config/pop/send-email.sh
```

**Usage:**
```bash
~/.config/pop/send-email.sh \
  recipient@example.com \
  "Subject Line" \
  "Email body message" \
  file1.pdf file2.pdf
```

---

## 🆘 Troubleshooting

### "Authentication failed" or "Invalid credentials"
- ✅ Check App Password is correct (16 characters)
- ✅ Ensure 2FA is enabled on your Google account
- ✅ Remove any spaces from the password
- ✅ Try generating a new App Password

### "Connection refused" or timeout
- ✅ Check SMTP host: `smtp.gmail.com`
- ✅ Check SMTP port: `587` (TLS)
- ✅ Verify your internet connection
- ✅ Check if your firewall blocks port 587

### Email not received
- ✅ Check recipient's spam folder
- ✅ Verify recipient email address is correct
- ✅ Test by sending to yourself first
- ✅ Check Gmail's "Sent" folder to verify it was sent

### "Could not open a new TTY"
- ✅ Make sure you loaded the environment: `source ~/.config/pop/.env`
- ✅ Ensure `POP_FROM` is set in your `.env` file

---

## 🔐 Security Best Practices

### ✅ DO:
- Keep `.env` file permissions at `600` (only you can read)
- Store App Password in `.env` file, not in scripts
- Use App Passwords, never your real Gmail password
- Keep `~/.config/pop/.env` out of version control

### ❌ DON'T:
- Never commit `.env` to git repositories
- Never share your App Password
- Never use your actual Gmail password
- Never make `.env` world-readable

### Git Safety (if using dotfiles repo):
```bash
# Add to .gitignore
echo ".env" >> ~/.config/pop/.gitignore
echo ".env.backup" >> ~/.config/pop/.gitignore
```

---

## 📚 Additional Resources

### Official Documentation
- **Pop GitHub**: https://github.com/charmbracelet/pop
- **Pop README**: https://github.com/charmbracelet/pop#readme
- **Charm Homepage**: https://charm.sh/

### Gmail Resources
- **App Passwords Guide**: https://support.google.com/accounts/answer/185833
- **2-Step Verification**: https://www.google.com/landing/2step/
- **Gmail Security Settings**: https://myaccount.google.com/security

### SMTP Reference
- **Gmail SMTP Settings**:
  - Host: `smtp.gmail.com`
  - Port: `587` (TLS) or `465` (SSL)
  - Authentication: Required (App Password)

---

## 🎯 Quick Reference Card

```bash
# Install
brew install pop

# Configure
mkdir -p ~/.config/pop
nano ~/.config/pop/.env  # Add SMTP settings
chmod 600 ~/.config/pop/.env

# Use
source ~/.config/pop/.env
pop --to recipient@example.com --subject "Hi" --body "Message"

# With attachments
pop --to recipient@example.com \
  --subject "Files" \
  --body "Attached" \
  --attach file.pdf
```

---

## ✨ Advanced: Integration with Claude Code

If you use Claude Code (Anthropic's CLI), you can create a `/pop-mail` command:

1. Create command file: `~/.claude/commands/pop-mail.md`
2. Add command specification (see [Claude Code docs](https://docs.claude.com/en/docs/claude-code))
3. Use natural language: "Send these PDFs via email"

This enables AI-powered email workflows! 🤖

---

## 📝 Summary

You've learned how to:
- ✅ Install Pop CLI
- ✅ Configure Gmail SMTP with App Password
- ✅ Send emails from terminal
- ✅ Attach files to emails
- ✅ Troubleshoot common issues
- ✅ Follow security best practices

**Need help?** Check the [Pop GitHub Issues](https://github.com/charmbracelet/pop/issues) or [Charm Discord](https://charm.sh/community)

---

**Happy emailing! 📧**

*Generated: 2025-11-03*
*Version: 1.0*
