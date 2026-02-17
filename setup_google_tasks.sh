#!/bin/bash
# Setup script for Google Tasks integration

set -e

echo "=== Google Tasks Integration Setup ==="
echo

# Check if Python packages are installed
echo "Checking dependencies..."
.venv/bin/python -c "import google.auth" 2>/dev/null || {
    echo "❌ Google Auth library not found"
    echo "Installing required packages..."
    .venv/bin/pip3 install --user google-auth-oauthlib google-auth-httplib2 google-api-python-client
}

echo "✓ Dependencies installed"
echo

# Install sync script
INSTALL_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/waybar-notes"

echo "Installing Google Tasks sync script..."
cp google_tasks_sync.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/google_tasks_sync.py"
echo "✓ Installed to $INSTALL_DIR/google_tasks_sync.py"
echo

# Setup instructions
echo "=== Google Cloud Console Setup ==="
echo
echo "To enable Google Tasks sync, you need OAuth2 credentials:"
echo
echo "1. Go to: https://console.cloud.google.com/"
echo
echo "2. Create a new project (or select existing)"
echo
echo "3. Enable the Google Tasks API:"
echo "   - Go to 'APIs & Services' > 'Library'"
echo "   - Search for 'Google Tasks API'"
echo "   - Click 'Enable'"
echo
echo "4. Create OAuth2 credentials:"
echo "   - Go to 'APIs & Services' > 'Credentials'"
echo "   - Click 'Create Credentials' > 'OAuth client ID'"
echo "   - Application type: 'Desktop app'"
echo "   - Name it whatever you like (e.g., 'Waybar Notes')"
echo "   - Click 'Create'"
echo
echo "5. Download the credentials:"
echo "   - Click the download icon next to your OAuth client"
echo "   - Save the file as: $CONFIG_DIR/credentials.json"
echo
echo "6. Run initial authentication:"
echo "   $INSTALL_DIR/google_tasks_sync.py --setup"
echo
echo "7. (Optional) Setup automatic sync:"
echo "   ./setup_auto_sync.sh"
echo
echo "=== Manual Sync Commands ==="
echo
echo "Pull from Google only (recommended for manual sync):"
echo "  google_tasks_sync.py --pull"
echo
echo "Push to Google only:"
echo "  google_tasks_sync.py --push"
echo
echo "Check sync status:"
echo "  google_tasks_sync.py"
echo
