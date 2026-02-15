#!/usr/bin/env python3
"""
Demo script - Adds sample notes for testing
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from notes_manager import NotesManager

def main():
    nm = NotesManager()
    
    # Clear existing notes
    nm.notes = []
    
    # Add sample notes
    sample_notes = [
        "Review pull requests for the authentication module",
        "Update project documentation",
        "Fix bug in user profile page",
        "Prepare slides for team meeting",
        "Write unit tests for API endpoints",
        "Deploy to staging environment",
        "Code review for new feature branch",
        "Optimize database queries"
    ]
    
    print("Adding sample notes...")
    for note_text in sample_notes:
        nm.add_note(note_text)
        print(f"  ✓ {note_text}")
    
    # Mark a couple as done
    nm.toggle_note(1)  # First note
    nm.toggle_note(3)  # Third note
    
    print(f"\nCreated {len(nm.notes)} sample notes")
    print(f"  • {len(nm.get_undone_notes())} undone")
    print(f"  • {len(nm.get_done_notes())} done")
    print("\nYou can now:")
    print("  1. Run ./waybar_notes.py to see the Waybar output")
    print("  2. Run ./notes_tui.py to open the terminal UI")

if __name__ == "__main__":
    main()
