#!/usr/bin/env python3
"""
Notes Manager - Backend for storing and managing notes
"""
import json
import os
from datetime import datetime
from pathlib import Path

NOTES_FILE = Path.home() / ".config" / "waybar-notes" / "notes.json"

class NotesManager:
    def __init__(self):
        self.notes_file = NOTES_FILE
        self.notes_file.parent.mkdir(parents=True, exist_ok=True)
        self.notes = self.load_notes()
    
    def load_notes(self):
        """Load notes from JSON file"""
        if self.notes_file.exists():
            try:
                with open(self.notes_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def save_notes(self):
        """Save notes to JSON file"""
        with open(self.notes_file, 'w') as f:
            json.dump(self.notes, f, indent=2)
    
    def add_note(self, text):
        """Add a new note"""
        note = {
            'id': self._generate_id(),
            'text': text,
            'done': False,
            'created': datetime.now().isoformat(),
            'completed': None
        }
        self.notes.append(note)
        self.save_notes()
        return note
    
    def toggle_note(self, note_id):
        """Toggle note done status"""
        for note in self.notes:
            if note['id'] == note_id:
                note['done'] = not note['done']
                note['completed'] = datetime.now().isoformat() if note['done'] else None
                self.save_notes()
                return True
        return False
    
    def delete_note(self, note_id):
        """Delete a note"""
        self.notes = [n for n in self.notes if n['id'] != note_id]
        self.save_notes()
    
    def get_undone_notes(self):
        """Get all undone notes"""
        return [n for n in self.notes if not n['done']]
    
    def get_done_notes(self):
        """Get all done notes"""
        return [n for n in self.notes if n['done']]
    
    def get_all_notes(self):
        """Get all notes"""
        return self.notes
    
    def _generate_id(self):
        """Generate unique ID for note"""
        if not self.notes:
            return 1
        return max(n['id'] for n in self.notes) + 1

if __name__ == "__main__":
    # Test the notes manager
    nm = NotesManager()
    print(f"Loaded {len(nm.notes)} notes")
    print(f"Undone: {len(nm.get_undone_notes())}")
    print(f"Done: {len(nm.get_done_notes())}")
