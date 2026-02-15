#!/usr/bin/env python3
"""
Waybar Notes Module - Displays cycling undone notes
"""
import json
import sys
from pathlib import Path
import time

# Add notes_manager to path
sys.path.insert(0, str(Path(__file__).parent))
from notes_manager import NotesManager

def escape_text(text):
    """Escape special characters for Waybar"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def truncate_text(text, max_length=50):
    """Truncate text if too long"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def main():
    nm = NotesManager()
    undone = nm.get_undone_notes()
    
    if not undone:
        output = {
            "text": "  No tasks",
            "tooltip": "Click to manage notes\nNo pending tasks",
            "class": "empty",
            "alt": "empty"
        }
    else:
        # Get current index based on time (cycle every 10 seconds)
        current_index = int(time.time() / 10) % len(undone)
        current_note = undone[current_index]
        
        # Build tooltip with all undone notes
        tooltip_lines = [f"📋 {len(undone)} pending task{'s' if len(undone) > 1 else ''}:", ""]
        for i, note in enumerate(undone):
            prefix = "▶ " if i == current_index else "  "
            tooltip_lines.append(f"{prefix}{escape_text(note['text'])}")
        
        output = {
            "text": f"📝 {escape_text(truncate_text(current_note['text'], 40))}",
            "tooltip": "\n".join(tooltip_lines),
            "class": "active",
            "alt": "active"
        }
    
    print(json.dumps(output))

if __name__ == "__main__":
    main()
