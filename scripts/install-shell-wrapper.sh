#!/usr/bin/env bash
#
# BARQUE Shell Wrapper Installation Script
# Installs barque-send to /usr/local/bin and sets up shell aliases

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}BARQUE Shell Wrapper Installer${NC}"
echo "================================"
echo ""

# Detect script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BARQUE_ROOT="$(dirname "$SCRIPT_DIR")"
WRAPPER_SCRIPT="$SCRIPT_DIR/barque-send"
INSTALL_PATH="/usr/local/bin/barque-send"

# Check if wrapper exists
if [ ! -f "$WRAPPER_SCRIPT" ]; then
    echo -e "${RED}✗ Error: barque-send script not found at $WRAPPER_SCRIPT${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1:${NC} Installing barque-send to /usr/local/bin/"

# Check if /usr/local/bin exists
if [ ! -d "/usr/local/bin" ]; then
    echo -e "${YELLOW}⚠ /usr/local/bin does not exist. Creating it...${NC}"
    sudo mkdir -p /usr/local/bin
fi

# Copy script
if sudo cp "$WRAPPER_SCRIPT" "$INSTALL_PATH"; then
    sudo chmod +x "$INSTALL_PATH"
    echo -e "${GREEN}✓ Installed: $INSTALL_PATH${NC}"
else
    echo -e "${RED}✗ Failed to install. You may need sudo privileges.${NC}"
    exit 1
fi

# Detect shell
SHELL_NAME=$(basename "$SHELL")
case "$SHELL_NAME" in
    zsh)
        SHELL_RC="$HOME/.zshrc"
        ;;
    bash)
        SHELL_RC="$HOME/.bashrc"
        ;;
    *)
        echo -e "${YELLOW}⚠ Unknown shell: $SHELL_NAME. Defaulting to ~/.bashrc${NC}"
        SHELL_RC="$HOME/.bashrc"
        ;;
esac

echo ""
echo -e "${BLUE}Step 2:${NC} Adding shell aliases to $SHELL_RC"

# Alias content
ALIAS_BLOCK="
# BARQUE Email Wrapper Aliases
alias bsend='barque-send'
alias bsend-light='barque-send --theme light'
alias bsend-dark='barque-send --theme dark'
alias bsend-quiet='barque-send --quiet'
"

# Check if aliases already exist
if grep -q "BARQUE Email Wrapper Aliases" "$SHELL_RC" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Aliases already exist in $SHELL_RC${NC}"
    echo "Skipping alias installation."
else
    echo "$ALIAS_BLOCK" >> "$SHELL_RC"
    echo -e "${GREEN}✓ Added aliases to $SHELL_RC${NC}"
    echo ""
    echo "Aliases added:"
    echo "  • bsend           → barque-send"
    echo "  • bsend-light     → barque-send --theme light"
    echo "  • bsend-dark      → barque-send --theme dark"
    echo "  • bsend-quiet     → barque-send --quiet"
fi

echo ""
echo -e "${BLUE}Step 3:${NC} Verifying installation"

# Check if installed
if command -v barque-send &> /dev/null; then
    echo -e "${GREEN}✓ barque-send is in PATH${NC}"
else
    echo -e "${YELLOW}⚠ barque-send not found in PATH. You may need to reload your shell.${NC}"
fi

# Check dependencies
echo ""
echo -e "${BLUE}Step 4:${NC} Checking dependencies"

if command -v barque &> /dev/null; then
    echo -e "${GREEN}✓ barque CLI found${NC}"
else
    echo -e "${YELLOW}⚠ barque CLI not found. Install with: pip install -e .${NC}"
fi

if command -v pop &> /dev/null; then
    echo -e "${GREEN}✓ Charm Pop found${NC}"
else
    echo -e "${YELLOW}⚠ Charm Pop not found. Install with: brew install pop${NC}"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Reload your shell configuration:"
echo -e "   ${YELLOW}source $SHELL_RC${NC}"
echo ""
echo "2. Set default recipient (optional but recommended):"
echo -e "   ${YELLOW}barque user-config set email.to colleague@example.com${NC}"
echo ""
echo "3. Send your first email:"
echo -e "   ${YELLOW}barque-send report.md${NC}"
echo -e "   ${YELLOW}bsend report.md${NC}  (using alias)"
echo ""
echo "4. Get help:"
echo -e "   ${YELLOW}barque-send --help${NC}"
echo ""
echo -e "📚 Full documentation: ${BLUE}docs/SHELL-SCRIPT-GUIDE.md${NC}"
echo ""
