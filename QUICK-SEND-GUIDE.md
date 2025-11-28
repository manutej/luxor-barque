# BARQUE Quick Send Guide

**One-line PDF generation and email delivery** 📧

---

## 🚀 Quick Start (60 seconds)

```bash
# 1. Install shell wrapper
cd /path/to/BARQUE
./scripts/install-shell-wrapper.sh

# 2. Set defaults (one-time)
barque user-config set email.to your-colleague@example.com
barque user-config set email.from you@example.com
barque user-config set email.resend_api_key "re_your_key_here"

# 3. Reload shell
source ~/.zshrc

# 4. Send your first PDF!
bsend report.md
```

✅ Done! Your colleague now has the PDF in both light and dark themes.

---

## 📋 Daily Usage

```bash
# Most common - send to default recipient
bsend report.md

# Send to someone else
bsend report.md boss@company.com

# Multiple recipients
bsend report.md --to ceo@company.com --to cfo@company.com

# Light theme only
bsend-light report.md

# Dark theme only
bsend-dark report.md

# Quiet mode (minimal output)
bsend-quiet report.md
```

---

## ⚙️ Configuration

```bash
# View current settings
barque user-config show

# Set default recipient
barque user-config set email.to colleague@example.com

# Set default sender
barque user-config set email.from you@example.com

# Set Resend API key
barque user-config set email.resend_api_key "re_abc123"

# Set default theme
barque user-config set preferences.theme both  # or light, dark

# Get specific value
barque user-config get email.to
```

---

## 🎯 Common Patterns

### Daily Standup
```bash
alias standup='bsend ~/notes/standup-$(date +%Y-%m-%d).md'
standup  # That's it!
```

### Weekly Report
```bash
alias weekly='bsend ~/reports/weekly.md boss@company.com --subject "Weekly Report - $(date +%b %d)"'
weekly
```

### Client Deliverables
```bash
bsend proposal.md client@example.com \
  --subject "Proposal: Q1 2024 Strategy" \
  --theme both
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `barque-send: command not found` | Run `./scripts/install-shell-wrapper.sh` |
| `No recipient specified` | Set default: `barque user-config set email.to user@example.com` |
| `Pop CLI not found` | Install: `brew install pop` |
| `Domain not verified` | Add domain at https://resend.com/domains |

---

## 📚 Full Documentation

- **Complete Guide:** `docs/SHELL-SCRIPT-GUIDE.md`
- **Implementation:** `docs/EMAIL-SIMPLIFICATION-SUMMARY.md`
- **Email Setup:** `docs/EMAIL-GUIDE.md`

---

## 💡 Pro Tips

1. **Set default recipient** for 90% fewer keystrokes
2. **Use aliases** (`bsend` instead of `barque-send`)
3. **Pre-configure API keys** in user config (never in scripts)
4. **Use `--quiet`** in automated scripts
5. **Create project-specific aliases** in `.env` files

---

## 🎨 Available Aliases

After installation, these aliases are available:

| Alias | Command | Use Case |
|-------|---------|----------|
| `bsend` | `barque-send` | General use |
| `bsend-light` | `barque-send --theme light` | Light theme only |
| `bsend-dark` | `barque-send --theme dark` | Dark theme only |
| `bsend-quiet` | `barque-send --quiet` | Minimal output |

---

## 🚀 Before vs After

### Before
```bash
export RESEND_API_KEY="re_abc123..."
barque generate report.md --theme both --output ./output
barque email output/light/report-light.pdf output/dark/report-dark.pdf \
  --to boss@company.com \
  --from you@company.com \
  --subject "Report" \
  --provider resend
```
**3 commands, 200+ characters** 😓

### After
```bash
bsend report.md
```
**1 command, 15 characters** 🎉

**90% reduction in effort!**

---

## ✅ Quick Checklist

- [ ] Install wrapper: `./scripts/install-shell-wrapper.sh`
- [ ] Set default recipient: `barque user-config set email.to user@example.com`
- [ ] Set Resend API key: `barque user-config set email.resend_api_key "re_..."`
- [ ] Reload shell: `source ~/.zshrc`
- [ ] Test: `bsend test.md`
- [ ] Create aliases for frequent recipients

---

**Questions?** Check `docs/SHELL-SCRIPT-GUIDE.md` for complete documentation.

**Status:** 🚀 Production Ready | **Version:** BARQUE v2.1.0
