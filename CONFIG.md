# BARQUE Configuration Guide

BARQUE uses **two types of configuration**:

1. **User Configuration** (`~/.config/barque/config.yaml`) - Personal settings like API keys
2. **Project Configuration** (`.barque/config.yaml`) - Project-specific settings like themes

---

## User Configuration

User configuration stores **personal settings** that should persist across all your BARQUE projects:
- API keys (Resend, SMTP)
- Default email addresses
- Personal preferences

### Location

```
~/.config/barque/config.yaml
```

On macOS/Linux, this follows the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html).

### Quick Setup

```bash
# 1. Create user config file with template
barque user-config init

# 2. Set your Resend API key
barque user-config set email.resend_api_key re_your_api_key_here

# 3. (Optional) Set default sender email
barque user-config set email.from your-email@example.com

# 4. Verify configuration
barque user-config show
```

### Available Settings

| Key | Description | Example |
|-----|-------------|---------|
| `email.resend_api_key` | Resend API key for email delivery | `re_abc123...` |
| `email.from` | Default sender email address | `user@example.com` |
| `email.signature` | Default email signature | `Sent with ❤️ by BARQUE` |
| `smtp.host` | SMTP server hostname | `smtp.gmail.com` |
| `smtp.port` | SMTP server port | `587` |
| `smtp.username` | SMTP username | `user@gmail.com` |
| `smtp.password` | SMTP password/app password | `your-app-password` |
| `preferences.theme` | Default theme | `both` / `light` / `dark` |
| `preferences.output` | Default output directory | `./output` |

### Management Commands

```bash
# Show config file location
barque user-config path

# Initialize with template
barque user-config init

# Set a value
barque user-config set email.resend_api_key re_abc123

# Get a value (sensitive values are masked)
barque user-config get email.resend_api_key

# Show all configuration
barque user-config show
```

### Manual Configuration

You can also edit the config file directly:

```bash
# Open in your editor
vim ~/.config/barque/config.yaml
# or
code ~/.config/barque/config.yaml
```

Example `config.yaml`:

```yaml
# Email settings for sending PDFs
email:
  resend_api_key: "re_your_api_key_here"
  default_from_email: "your-email@example.com"
  default_signature: "Sent with ❤️ by BARQUE"

# Preferences
preferences:
  default_theme: "both"
  default_output_dir: "./output"
```

---

## Getting a Resend API Key

BARQUE uses [Resend](https://resend.com) for reliable email delivery.

### Steps:

1. Go to https://resend.com and sign up
2. Navigate to **API Keys** in your dashboard
3. Click **Create API Key**
4. Copy your API key (starts with `re_`)
5. Set it in BARQUE:

```bash
barque user-config set email.resend_api_key re_your_key_here
```

### Free Tier

Resend's free tier includes:
- **100 emails/day**
- **3,000 emails/month**
- Perfect for personal and small team use

---

## Alternative: SMTP Configuration

If you prefer to use your own SMTP server (Gmail, Outlook, etc.), configure SMTP instead:

```bash
# Gmail example (requires App Password)
barque user-config set smtp.host smtp.gmail.com
barque user-config set smtp.port 587
barque user-config set smtp.username your-email@gmail.com
barque user-config set smtp.password your-app-password
```

**Gmail Setup:**
1. Enable 2-factor authentication
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password (not your regular password)

---

## Project Configuration

Project configuration is stored in `.barque/config.yaml` in your project directory.

### Initialize Project

```bash
# In your project directory
barque init
```

This creates `.barque/config.yaml` with project settings:
- Project name/description
- Output directory
- Theme colors
- PDF styling
- Processing options

### Manage Project Config

```bash
# Show project configuration
barque config --show

# Validate project configuration
barque config --validate
```

---

## Using BARQUE with Email

Once user configuration is set up, sending PDFs via email is simple:

### Generate and Send

```bash
# Generate PDF and send in one command
barque send document.md --to recipient@example.com

# With custom subject
barque send document.md \
  --to recipient@example.com \
  --subject "Monthly Report"
```

### Send Existing PDF

```bash
# Send already-generated PDF
barque email output/light/document-light.pdf \
  --to recipient@example.com \
  --subject "Report"
```

### Multiple Recipients

```bash
barque send document.md \
  --to alice@example.com \
  --to bob@example.com \
  --to charlie@example.com
```

---

## Security Best Practices

### API Keys

✅ **DO:**
- Store API keys in `~/.config/barque/config.yaml`
- Keep this file private (should not be committed to git)
- Use environment-specific API keys (dev/prod)

❌ **DON'T:**
- Commit API keys to version control
- Share your config file publicly
- Use production API keys in development

### File Permissions

Ensure your config file is only readable by you:

```bash
chmod 600 ~/.config/barque/config.yaml
```

---

## Troubleshooting

### Email Not Sending

1. **Check if config exists:**
   ```bash
   barque user-config path
   ```

2. **Verify API key is set:**
   ```bash
   barque user-config show
   ```

3. **Test Pop CLI directly:**
   ```bash
   pop --version
   ```

4. **Check Pop can access the key:**
   ```bash
   # Manually test with Pop
   echo "Test message" | pop \
     --to test@example.com \
     --subject "Test" \
     --resend.key re_your_key
   ```

### Config File Not Found

If BARQUE can't find your config:

```bash
# Show where it's looking
barque user-config path

# Create fresh config
barque user-config init
```

### Permission Denied

If you get permission errors:

```bash
# Fix permissions
chmod 700 ~/.config/barque
chmod 600 ~/.config/barque/config.yaml
```

---

## Environment Variables (Advanced)

You can also use environment variables to override config:

```bash
# Override Resend API key
export RESEND_API_KEY=re_your_key_here

# Override sender email
export POP_FROM=your-email@example.com

# Then use barque normally
barque send document.md --to recipient@example.com
```

**Precedence (highest to lowest):**
1. Command-line flags (`--resend-api-key`)
2. Environment variables (`RESEND_API_KEY`)
3. User config (`~/.config/barque/config.yaml`)
4. Defaults

---

## Examples

### Complete Setup Workflow

```bash
# 1. Install BARQUE and Pop
brew install pop
pip install barque

# 2. Set up user configuration
barque user-config init
barque user-config set email.resend_api_key re_abc123
barque user-config set email.from myname@example.com

# 3. Verify setup
barque user-config show

# 4. Initialize a project
cd my-project
barque init

# 5. Generate and send a report
barque send report.md \
  --to team@example.com \
  --subject "Weekly Report"
```

### Team Workflow

**Setup (once per user):**
```bash
# Each team member sets their own API key
barque user-config init
barque user-config set email.resend_api_key $THEIR_API_KEY
```

**Daily use:**
```bash
# Everyone shares the same project config (.barque/)
git clone project-repo
cd project-repo

# Generate PDFs
barque generate report.md

# Send using their own email credentials
barque send report.md --to client@example.com
```

---

## Summary

| Config Type | Location | Purpose | Committed to Git? |
|------------|----------|---------|-------------------|
| **User Config** | `~/.config/barque/config.yaml` | API keys, personal settings | ❌ No (private) |
| **Project Config** | `.barque/config.yaml` | Project theme, styling | ✅ Yes (shared) |

**Key Points:**
- User config = personal/private settings
- Project config = shared team settings
- Always set API keys in user config
- Use `barque user-config` to manage API keys
- Use `barque config` to manage project settings

---

## Getting Help

```bash
# General help
barque --help

# User config help
barque user-config --help

# Command-specific help
barque send --help
barque email --help
```

**Resources:**
- BARQUE Documentation: `/BARQUE/README.md`
- Resend Documentation: https://resend.com/docs
- Pop CLI: https://github.com/charmbracelet/pop
