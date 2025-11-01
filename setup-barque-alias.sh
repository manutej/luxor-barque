#!/bin/bash

# BARQUE Shell Alias Setup Script
# Adds barque command to your shell configuration

BARQUE_DIR="/Users/manu/Documents/LUXOR/PROJECTS/BARQUE"
VENV_PATH="$BARQUE_DIR/venv/bin/barque"

# Detect shell
SHELL_NAME=$(basename "$SHELL")

# Determine config file
case "$SHELL_NAME" in
    bash)
        CONFIG_FILE="$HOME/.bashrc"
        ;;
    zsh)
        CONFIG_FILE="$HOME/.zshrc"
        ;;
    *)
        echo "⚠️  Unknown shell: $SHELL_NAME"
        echo "Please manually add the alias to your shell config:"
        echo "alias barque='$VENV_PATH'"
        exit 1
        ;;
esac

# Check if alias already exists
if grep -q "alias barque=" "$CONFIG_FILE" 2>/dev/null; then
    echo "⚠️  BARQUE alias already exists in $CONFIG_FILE"
    echo "Skipping..."
    exit 0
fi

# Add alias
echo "" >> "$CONFIG_FILE"
echo "# BARQUE - Beautiful Automated Report and Query Universal Engine" >> "$CONFIG_FILE"
echo "alias barque='$VENV_PATH'" >> "$CONFIG_FILE"

echo "✅ BARQUE alias added to $CONFIG_FILE"
echo ""
echo "To use immediately, run:"
echo "  source $CONFIG_FILE"
echo ""
echo "Or simply open a new terminal window."
echo ""
echo "Test with:"
echo "  barque --version"
echo "  barque --help"
