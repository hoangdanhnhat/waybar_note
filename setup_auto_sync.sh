#!/bin/bash
# Setup automatic syncing with systemd

set -e

echo "=== Setting up Automatic Sync ==="
echo

SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

# Create systemd user directory
mkdir -p "$SYSTEMD_USER_DIR"

# Copy service and timer files
echo "Installing systemd service and timer..."
cp waybar-notes-sync.service "$SYSTEMD_USER_DIR/"
cp waybar-notes-sync.timer "$SYSTEMD_USER_DIR/"

echo "✓ Service files installed"
echo

# Reload systemd
echo "Reloading systemd..."
systemctl --user daemon-reload

echo "✓ Systemd reloaded"
echo

# Enable and start the timer
echo "Enabling automatic sync..."
systemctl --user enable waybar-notes-sync.timer
systemctl --user start waybar-notes-sync.timer

echo "✓ Automatic sync enabled"
echo

# Show status
echo "=== Sync Status ==="
systemctl --user status waybar-notes-sync.timer --no-pager

echo
echo "=== Configuration ==="
echo "Sync interval: Every 5 minutes"
echo
echo "To change the interval, edit:"
echo "  $SYSTEMD_USER_DIR/waybar-notes-sync.timer"
echo
echo "Then reload with:"
echo "  systemctl --user daemon-reload"
echo "  systemctl --user restart waybar-notes-sync.timer"
echo
echo "=== Useful Commands ==="
echo "Check sync status:"
echo "  systemctl --user status waybar-notes-sync.timer"
echo
echo "View sync logs:"
echo "  journalctl --user -u waybar-notes-sync.service -f"
echo
echo "Trigger manual sync:"
echo "  systemctl --user start waybar-notes-sync.service"
echo
echo "Disable automatic sync:"
echo "  systemctl --user stop waybar-notes-sync.timer"
echo "  systemctl --user disable waybar-notes-sync.timer"
echo
echo "✅ Automatic sync setup complete!"
