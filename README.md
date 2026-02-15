# Waybar Notes Manager

A sleek, efficient notes/task manager for Waybar that helps you stay on top of your todos without leaving your bar.

## Features

- **Auto-cycling display**: Rotates through undone tasks every 10 seconds
- **Hover preview**: See all pending tasks in a tooltip on hover
- **Fast TUI interface**: Terminal-based UI for quick task management
- **Three view modes**: Undone, Done, and All tasks
- **Vim-style navigation**: j/k or arrow keys for navigation
- **Persistent storage**: JSON-based storage in ~/.config/waybar-notes
- **Smooth updates**: Real-time updates every second

## Installation

### Quick Install

```bash
chmod +x install.sh
./install.sh
```

### Manual Installation

1. Copy the Python scripts to a location in your PATH:
```bash
mkdir -p ~/.local/bin
cp notes_manager.py waybar_notes.py notes_tui.py ~/.local/bin/
chmod +x ~/.local/bin/waybar_notes.py ~/.local/bin/notes_tui.py
```

2. Create the config directory:
```bash
mkdir -p ~/.config/waybar-notes
echo "[]" > ~/.config/waybar-notes/notes.json
```

## Waybar Configuration

### 1. Add to config.json

Edit `~/.config/waybar/config.json` and add the custom module:

```json
{
    "custom/notes": {
        "exec": "$HOME/.local/bin/waybar_notes.py",
        "return-type": "json",
        "interval": 1,
        "format": "{}",
        "on-click": "alacritty -e $HOME/.local/bin/notes_tui.py",
        "tooltip": true
    }
}
```

Then add `"custom/notes"` to your modules list:
```json
"modules-right": ["custom/notes", "clock", "tray"]
```

**Note**: Replace `alacritty` with your preferred terminal:
- kitty: `"kitty -e $HOME/.local/bin/notes_tui.py"`
- foot: `"foot -e $HOME/.local/bin/notes_tui.py"`
- wezterm: `"wezterm -e $HOME/.local/bin/notes_tui.py"`
- gnome-terminal: `"gnome-terminal -- $HOME/.local/bin/notes_tui.py"`

### 2. Add CSS Styling

Add the contents of `waybar-style.css` to `~/.config/waybar/style.css`.

### 3. Restart Waybar

```bash
killall waybar && waybar &
```

## Usage

### Waybar Module

- **View**: The module displays the current task, cycling every 10 seconds
- **Hover**: Hover over the module to see all undone tasks
- **Click**: Click to open the terminal UI

### Terminal UI (TUI)

#### Navigation
- `↑` / `↓` or `j` / `k` - Move up/down
- `Tab` - Switch between views (Undone → Done → All)
- `Space` - Toggle task completion status
- `n` - Create new note
- `d` - Delete selected note
- `q` - Quit

#### Views
1. **Undone**: Shows only incomplete tasks
2. **Done**: Shows only completed tasks
3. **All**: Shows all tasks

#### Creating Notes
1. Press `n` to enter input mode
2. Type your note text
3. Press `Enter` to save or `Esc` to cancel

#### Managing Notes
- Toggle completion: Select a note and press `Space`
- Delete: Select a note and press `d`

## File Structure

```
~/.local/bin/
├── notes_manager.py    # Core note management logic
├── waybar_notes.py     # Waybar module script
└── notes_tui.py        # Terminal UI

~/.config/waybar-notes/
└── notes.json          # Notes database
```

## Data Format

Notes are stored in JSON format at `~/.config/waybar-notes/notes.json`:

```json
[
  {
    "id": 1,
    "text": "Complete project documentation",
    "done": false,
    "created": "2024-02-16T10:30:00",
    "completed": null
  },
  {
    "id": 2,
    "text": "Review pull requests",
    "done": true,
    "created": "2024-02-16T09:00:00",
    "completed": "2024-02-16T11:30:00"
  }
]
```

## Customization

### Cycling Interval

To change the cycling interval, edit `waybar_notes.py` and modify this line:
```python
current_index = int(time.time() / 10) % len(undone)  # Change 10 to desired seconds
```

### Module Update Interval

In your Waybar config, adjust the `interval` value:
```json
"interval": 1  // Update every second (recommended for smooth cycling)
```

### Styling

The CSS uses a semi-transparent background with blue accents. You can customize:
- Colors: Change the rgba() and hex values
- Transitions: Modify the transition timing
- Hover effects: Adjust transform and box-shadow

## Troubleshooting

### Module not appearing
1. Check that scripts are executable: `ls -l ~/.local/bin/waybar_notes.py`
2. Test the script directly: `~/.local/bin/waybar_notes.py`
3. Check Waybar logs: `journalctl -xe | grep waybar`

### Terminal UI not opening
1. Verify your terminal emulator is installed
2. Test directly: `~/.local/bin/notes_tui.py`
3. Check the on-click command in config.json

### Notes not saving
1. Check permissions: `ls -ld ~/.config/waybar-notes`
2. Verify JSON is valid: `cat ~/.config/waybar-notes/notes.json | python3 -m json.tool`

## Requirements

- Python 3.6+
- Waybar
- A terminal emulator (alacritty, kitty, foot, etc.)
- curses library (usually included with Python)

## License

This project is released into the public domain. Feel free to use, modify, and distribute as you see fit.

## Tips

- Keep notes short (under 50 characters) for best display
- Use the Undone view to focus on what needs to be done
- Press `Tab` repeatedly to quickly switch between views
- The cycling helps you remember tasks you might have forgotten
