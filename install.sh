#!/bin/bash
# Installation script for Waybar Notes Manager

set -e

echo "=== Waybar Notes Manager Installation ==="
echo

# Determine installation directory
INSTALL_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/waybar-notes"

echo "Installation directory: $INSTALL_DIR"
echo "Configuration directory: $CONFIG_DIR"
echo

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing scripts..."
# Copy and make executable
cp "$SCRIPT_DIR/notes_manager.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/waybar_notes.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/notes_tui.py" "$INSTALL_DIR/"

chmod +x "$INSTALL_DIR/notes_manager.py"
chmod +x "$INSTALL_DIR/waybar_notes.py"
chmod +x "$INSTALL_DIR/notes_tui.py"

echo "✓ Scripts installed to $INSTALL_DIR"
echo

# Initialize empty notes file
if [ ! -f "$CONFIG_DIR/notes.json" ]; then
    echo "[]" > "$CONFIG_DIR/notes.json"
    echo "✓ Created notes database at $CONFIG_DIR/notes.json"
else
    echo "✓ Notes database already exists"
fi
echo

# Show Waybar configuration instructions
echo "=== Waybar Configuration ==="
echo
echo "1. Add this to your ~/.config/waybar/config.json:"
echo
cat << 'EOF'
"custom/notes": {
    "exec": "$HOME/.local/bin/waybar_notes.py",
    "return-type": "json",
    "interval": 1,
    "format": "{}",
    "on-click": "alacritty -e $HOME/.local/bin/notes_tui.py",
    "tooltip": true
}
EOF
echo
echo "   Then add \"custom/notes\" to your modules list."
echo
echo "2. Add the CSS from waybar-style.css to ~/.config/waybar/style.css"
echo
echo "3. Restart Waybar:"
echo "   killall waybar && waybar &"
echo
echo "=== Usage ==="
echo
echo "• The module will automatically cycle through undone tasks every 10 seconds"
echo "• Hover over the module to see all undone tasks"
echo "• Click the module to open the terminal UI"
echo
echo "Terminal UI controls:"
echo "  ↑/↓ or j/k: Navigate"
echo "  Tab: Switch between Undone/Done/All views"
echo "  Space: Toggle task completion"
echo "  N: Create new note"
echo "  D: Delete selected note"
echo "  Q: Quit"
echo
echo "=== Installation Complete! ==="
