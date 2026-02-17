# Google Tasks Integration Guide

Complete guide to syncing your Waybar notes with Google Tasks for seamless cross-device task management.

## Features

- ✅ **Bidirectional Sync**: Changes sync both ways between local and Google Tasks
- ✅ **All Task Lists**: Syncs with ALL your Google Task lists, not just one
- ✅ **Automatic Sync**: Optional systemd timer syncs every 5 minutes
- ✅ **Manual Sync**: Sync on-demand with simple commands
- ✅ **OAuth2 Authentication**: Secure Google authentication
- ✅ **Conflict-Free**: Server (Google) is source of truth during conflicts

## Quick Start

### 1. Install Dependencies

```bash
pip3 install --user --break-system-packages google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Get Google OAuth2 Credentials

#### Step-by-Step:

1. **Go to Google Cloud Console**: https://console.cloud.google.com/

2. **Create a Project** (or select existing):
   - Click "Select a project" dropdown
   - Click "New Project"
   - Name it (e.g., "Waybar Notes")
   - Click "Create"

3. **Enable Google Tasks API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Tasks API"
   - Click on it and press "Enable"

4. **Create OAuth2 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - If prompted, configure the OAuth consent screen:
     - User Type: "External"
     - App name: "Waybar Notes"
     - User support email: your email
     - Developer contact: your email
     - Click "Save and Continue" through the scopes and test users
   - Back to "Create OAuth client ID":
     - Application type: **Desktop app**
     - Name: "Waybar Notes Client"
     - Click "Create"

5. **Download Credentials**:
   - Click the download icon (⬇) next to your new OAuth client
   - This downloads a JSON file
   - Rename and move it:
     ```bash
     mv ~/Downloads/client_secret_*.json ~/.config/waybar-notes/credentials.json
     ```

### 3. Initial Setup & Authentication

```bash
# Run the setup script
./setup_google_tasks.sh

# Authenticate (opens browser)
~/.local/bin/google_tasks_sync.py --setup
```

This will:
- Open your browser for Google login
- Ask you to authorize the app
- Save your credentials locally

### 4. (Optional) Enable Automatic Sync

```bash
./setup_auto_sync.sh
```

This sets up a systemd timer that syncs every 5 minutes automatically.

## Usage

### Automatic Syncing in TUI

The Terminal UI (TUI) now includes automatic syncing:

- **On Startup**: When you open the TUI, it automatically pulls the latest tasks from Google Tasks
- **On Close**: When you close the TUI (press Q), any changes you made are automatically synced back to Google Tasks
- **Smart Sync**: If you only view tasks without making changes, the TUI closes instantly without syncing

This means you don't need to manually run sync commands in most cases!

### Manual Sync Commands

For advanced usage, you can still run manual sync commands:

```bash
# Pull from Google Tasks only (recommended for manual sync)
google_tasks_sync.py --pull

# Push to Google Tasks only
google_tasks_sync.py --push

# Check sync status
google_tasks_sync.py
```

### How Syncing Works

1. **Initial Setup** (`--setup`):
   - Authenticates with Google Tasks
   - Downloads all tasks from ALL your Google Task lists
   - Creates local notes for all Google tasks
   - Sets up ID mapping to track which notes match which tasks

2. **Pull Only** (`--pull`) - True Mirror Sync:
   - Downloads tasks from ALL Google Task lists
   - Creates new local notes for new Google tasks
   - Updates existing notes that have changed
   - **Deletes local notes that no longer exist in Google Tasks**
   - This creates a true mirror of Google Tasks on your local machine
   - Used automatically by the TUI on startup
   - Use this for manual syncs from Google

3. **Push Only** (`--push`):
   - Uploads local notes to Google Tasks
   - Creates new Google tasks in your default list for new notes
   - Updates existing tasks that have changed
   - Used automatically by the TUI on close (if changes were made)

### Automatic Sync Timer (Optional)

In addition to automatic TUI syncing, if you enabled automatic sync, your notes will sync every 5 minutes via systemd:

```bash
# Check sync status
systemctl --user status waybar-notes-sync.timer

# View sync logs (live)
journalctl --user -u waybar-notes-sync.service -f

# Trigger immediate sync
systemctl --user start waybar-notes-sync.service

# Stop automatic sync
systemctl --user stop waybar-notes-sync.timer
systemctl --user disable waybar-notes-sync.timer
```

**Note**: The TUI already syncs automatically on startup and close, so the timer is mainly useful if you want background syncing without opening the TUI.

### Changing Sync Interval

Edit the timer file:
```bash
nano ~/.config/systemd/user/waybar-notes-sync.timer
```

Change this line:
```ini
OnUnitActiveSec=5min  # Change to 10min, 30min, 1h, etc.
```

Then reload:
```bash
systemctl --user daemon-reload
systemctl --user restart waybar-notes-sync.timer
```

## Files & Storage

### Local Files
```
~/.config/waybar-notes/
├── notes.json          # Your notes database
├── credentials.json    # OAuth2 credentials (from Google)
├── token.pickle        # Authentication token (auto-generated)
└── sync_state.json     # Sync mapping (auto-generated)
```

### Google Tasks
- Syncs with ALL your task lists
- Each local note maps to one Google Task
- New local notes get added to your default (first) task list
- Tasks from any list can be edited locally
- Completion status syncs both ways

## Troubleshooting

### "credentials.json not found"
Make sure you downloaded the OAuth2 credentials from Google Cloud Console and placed them at:
```bash
~/.config/waybar-notes/credentials.json
```

### "Authentication failed"
Delete the token and re-authenticate:
```bash
rm ~/.config/waybar-notes/token.pickle
google_tasks_sync.py --setup
```

### "API not enabled"
Make sure you enabled the Google Tasks API in Google Cloud Console:
1. Go to https://console.cloud.google.com/
2. Select your project
3. Go to "APIs & Services" > "Library"
4. Search "Google Tasks API"
5. Click "Enable"

### Sync conflicts
The sync uses "server wins" strategy - Google Tasks is the source of truth. If there's a conflict:
- Pull from Google first
- Then local changes push

### Check sync logs
```bash
# View recent sync attempts
journalctl --user -u waybar-notes-sync.service -n 50

# Watch live sync
journalctl --user -u waybar-notes-sync.service -f
```

## Security Notes

- **credentials.json**: Contains your OAuth2 client ID and secret
- **token.pickle**: Contains your access/refresh tokens
- Keep these files secure (they're in your home directory)
- Never commit these to git or share them
- The app only requests access to Google Tasks (no other data)

## Uninstalling

### Remove automatic sync:
```bash
systemctl --user stop waybar-notes-sync.timer
systemctl --user disable waybar-notes-sync.timer
rm ~/.config/systemd/user/waybar-notes-sync.*
systemctl --user daemon-reload
```

### Remove credentials:
```bash
rm ~/.config/waybar-notes/credentials.json
rm ~/.config/waybar-notes/token.pickle
rm ~/.config/waybar-notes/sync_state.json
```

### Revoke app access in Google:
1. Go to https://myaccount.google.com/permissions
2. Find "Waybar Notes"
3. Click "Remove access"

## Tips

- ✅ The TUI automatically syncs on startup and close - you don't need to do anything!
- ✅ If you only view tasks without making changes, the TUI closes instantly
- ✅ Use Google Tasks app on mobile to add tasks to any list
- ✅ All tasks from all lists appear in your local notes
- ✅ New local notes created in the TUI get added to your default (first) task list
- ✅ You can organize tasks in different lists in Google Tasks, they all sync
- ✅ Works offline - changes are saved locally and synced when you have internet
- ✅ Optional: Enable automatic 5-minute sync timer for background syncing
- ✅ Manual sync with `google_tasks_sync.py --pull` anytime if needed

## FAQ

**Q: Can I use multiple devices?**  
A: Yes! Set up the sync on each device and they'll all stay in sync via Google Tasks.

**Q: What happens if I delete a task in Google Tasks?**  
A: On next sync, it will be removed from your local notes too.

**Q: Which task list do new local notes go to?**  
A: New notes created locally get added to your default (first) task list in Google Tasks. You can then move them to other lists in the Google Tasks app.

**Q: Can I have tasks in multiple Google Task lists?**  
A: Yes! All tasks from ALL your Google Task lists sync to your local notes. You can organize them however you want in Google Tasks.

**Q: Does it work offline?**  
A: Yes! Local notes work offline. When you open the TUI without internet, you'll see a warning. Changes are saved locally and will sync automatically the next time you have an internet connection and open the TUI.

**Q: How do I know if sync is working?**  
A: Run `google_tasks_sync.py` to see last sync time and which lists are syncing, or check the systemd service status.