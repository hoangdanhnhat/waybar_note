#!/usr/bin/env python3
"""
Notes Manager TUI - Terminal interface for managing notes
"""
import curses
import sys
import subprocess
import socket
import threading
import time
from pathlib import Path
from datetime import datetime

# Add notes_manager to path
sys.path.insert(0, str(Path(__file__).parent))
from notes_manager import NotesManager

def check_internet_connection():
    """Check if internet is available"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except (socket.timeout, socket.error):
        return False

class NotesTUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.nm = NotesManager()
        self.current_tab = 0  # 0 = Undone, 1 = Done, 2 = All
        self.selected_idx = 0
        self.scroll_offset = 0
        self.input_mode = False
        self.input_buffer = ""
        self.has_internet = check_internet_connection()
        self.notes_modified = False  # Track if notes were changed
        
        # Initialize colors
        curses.start_color()
        curses.use_default_colors()  # Use terminal default colors
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected
        curses.init_pair(2, curses.COLOR_GREEN, -1)  # Done
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Undone
        curses.init_pair(4, curses.COLOR_CYAN, -1)  # Header
        curses.init_pair(5, curses.COLOR_RED, -1)  # Delete
        
        curses.curs_set(0)  # Hide cursor
        self.stdscr.keypad(True)
        self.stdscr.timeout(100)  # Non-blocking with 100ms timeout
        
        # Enable flicker-free updates
        try:
            curses.cbreak()
            self.stdscr.nodelay(False)
            self.stdscr.timeout(100)
        except:
            pass
        
        # On startup: if internet, pull from Google Tasks
        if self.has_internet:
            self.show_syncing_message()
            self.pull_from_google()
            self.notes_modified = False  # Reset after pulling
            time.sleep(0.5)  # Brief delay to let user see the message
        else:
            # Show warning if no internet
            self.show_warning_dialog(
                "No Internet Connection",
                "Changes made locally will NOT be synced to Google Tasks",
                "and will be LOST the next time you open the app with internet!"
            )
    
    def get_current_notes(self):
        """Get notes for current tab"""
        if self.current_tab == 0:
            return self.nm.get_undone_notes()
        elif self.current_tab == 1:
            return self.nm.get_done_notes()
        else:
            return self.nm.get_all_notes()
    
    def pull_from_google(self):
        """Pull tasks from Google Tasks"""
        # Try multiple possible locations for the sync script
        possible_paths = [
            Path.home() / ".local/bin/google_tasks_sync.py",
            Path(__file__).parent / "google_tasks_sync.py",
        ]
        
        sync_script = None
        for path in possible_paths:
            if path.exists():
                sync_script = path
                break
        
        if sync_script:
            try:
                result = subprocess.run([str(sync_script), "--pull"], 
                                      capture_output=True, timeout=30)
                # Reload notes from file
                self.nm.notes = self.nm.load_notes()
                self.selected_idx = 0
                self.scroll_offset = 0
            except Exception as e:
                # Sync failed silently, but continue with existing notes
                pass
        else:
            # Sync script not found, continue with existing notes
            pass
    
    def push_to_google(self):
        """Push tasks to Google Tasks"""
        # Try multiple possible locations for the sync script
        possible_paths = [
            Path.home() / ".local/bin/google_tasks_sync.py",
            Path(__file__).parent / "google_tasks_sync.py",
        ]
        
        sync_script = None
        for path in possible_paths:
            if path.exists():
                sync_script = path
                break
        
        if sync_script:
            try:
                subprocess.run([str(sync_script), "--push"], 
                             capture_output=True, timeout=30)
            except Exception as e:
                # Log the error even if we can't display it
                pass
        else:
            # Script not found at any expected location
            pass
    
    def show_warning_dialog(self, title, line1, line2):
        """Show a warning dialog that pauses for user to read"""
        height, width = self.stdscr.getmaxyx()
        
        # Loop until ENTER or Q is pressed
        while True:
            self.stdscr.erase()
            
            # Draw warning box
            box_width = min(70, width - 4)
            box_height = 11
            start_x = (width - box_width) // 2
            start_y = (height - box_height) // 2
            
            # Draw border
            self.stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            for i in range(box_height):
                self.stdscr.addstr(start_y + i, start_x, "║" + " " * (box_width - 2) + "║")
            self.stdscr.addstr(start_y, start_x, "╔" + "═" * (box_width - 2) + "╗")
            self.stdscr.addstr(start_y + box_height - 1, start_x, "╚" + "═" * (box_width - 2) + "╝")
            self.stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            
            # Draw title
            self.stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            title_x = start_x + (box_width - len(title)) // 2
            self.stdscr.addstr(start_y + 1, title_x, title)
            self.stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            
            # Draw message
            msg_y = start_y + 3
            self.stdscr.addstr(msg_y, start_x + 2, line1[:box_width - 4])
            self.stdscr.addstr(msg_y + 1, start_x + 2, line2[:box_width - 4])
            
            # Draw instruction
            instr = "Press ENTER to continue or Q to quit"
            instr_x = start_x + (box_width - len(instr)) // 2
            self.stdscr.attron(curses.A_DIM)
            self.stdscr.addstr(start_y + box_height - 2, instr_x, instr)
            self.stdscr.attroff(curses.A_DIM)
            
            self.stdscr.refresh()
            key = self.stdscr.getch()  # Wait for key press
            
            if key == 10 or key == curses.KEY_ENTER:  # ENTER key
                break
            elif key == ord('q') or key == ord('Q'):  # Q key - quit
                sys.exit(0)
    
    def show_info_message(self, message):
        """Show a brief info message"""
        height, width = self.stdscr.getmaxyx()
        self.stdscr.erase()
        msg_x = (width - len(message)) // 2
        msg_y = height // 2
        self.stdscr.attron(curses.color_pair(4))
        self.stdscr.addstr(msg_y, msg_x, message)
        self.stdscr.attroff(curses.color_pair(4))
        self.stdscr.refresh()
    
    def show_syncing_message(self):
        """Show syncing message with loading animation"""
        height, width = self.stdscr.getmaxyx()
        self.stdscr.erase()
        
        message = "Syncing from Google Tasks..."
        msg_x = (width - len(message)) // 2
        msg_y = height // 2
        
        self.stdscr.attron(curses.color_pair(4))
        self.stdscr.addstr(msg_y, msg_x, message)
        self.stdscr.attroff(curses.color_pair(4))
        self.stdscr.refresh()
    
    def show_warning_on_close(self):
        """Show warning when closing without internet"""
        height, width = self.stdscr.getmaxyx()
        
        # Loop until ENTER is pressed
        while True:
            self.stdscr.erase()
            
            # Draw warning box
            box_width = min(75, width - 4)
            box_height = 12
            start_x = (width - box_width) // 2
            start_y = (height - box_height) // 2
            
            # Draw border
            self.stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            for i in range(box_height):
                self.stdscr.addstr(start_y + i, start_x, "║" + " " * (box_width - 2) + "║")
            self.stdscr.addstr(start_y, start_x, "╔" + "═" * (box_width - 2) + "╗")
            self.stdscr.addstr(start_y + box_height - 1, start_x, "╚" + "═" * (box_width - 2) + "╝")
            self.stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            
            # Draw title
            title = "No Internet Connection"
            self.stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            title_x = start_x + (box_width - len(title)) // 2
            self.stdscr.addstr(start_y + 1, title_x, title)
            self.stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            
            # Draw message
            msg_y = start_y + 3
            lines = [
                "All changes made locally will be LOST",
                "the next time you open the app with",
                "an internet connection!"
            ]
            for i, line in enumerate(lines):
                self.stdscr.addstr(msg_y + i, start_x + 2, line[:box_width - 4])
            
            # Draw note
            note = "Notes are saved locally for waybar widget usage."
            self.stdscr.attron(curses.A_DIM)
            self.stdscr.addstr(msg_y + 4, start_x + 2, note[:box_width - 4])
            self.stdscr.attroff(curses.A_DIM)
            
            # Draw instruction
            instr = "Press ENTER to exit"
            instr_x = start_x + (box_width - len(instr)) // 2
            self.stdscr.attron(curses.A_DIM)
            self.stdscr.addstr(start_y + box_height - 2, instr_x, instr)
            self.stdscr.attroff(curses.A_DIM)
            
            self.stdscr.refresh()
            key = self.stdscr.getch()  # Wait for key press
            
            if key == 10 or key == curses.KEY_ENTER:  # ENTER key
                break
    
    def draw_header(self):
        """Draw the header with tabs"""
        height, width = self.stdscr.getmaxyx()
        tabs = ["UNDONE", "DONE", "ALL"]
        
        self.stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
        self.stdscr.addstr(0, 0, "═" * width)
        self.stdscr.addstr(1, 2, "📝 NOTES MANAGER")
        self.stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
        
        # Draw tabs
        x_pos = 2
        for i, tab in enumerate(tabs):
            if i == self.current_tab:
                self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                self.stdscr.addstr(2, x_pos, f" {tab} ")
                self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
            else:
                self.stdscr.addstr(2, x_pos, f" {tab} ")
            x_pos += len(tab) + 3
        
        self.stdscr.attron(curses.color_pair(4))
        self.stdscr.addstr(3, 0, "─" * width)
        self.stdscr.attroff(curses.color_pair(4))
    
    def draw_notes(self):
        """Draw the list of notes"""
        height, width = self.stdscr.getmaxyx()
        notes = self.get_current_notes()
        
        # Calculate visible area
        visible_start = 4
        visible_height = height - 7  # Leave space for header and footer
        
        if not notes:
            msg = "No notes in this category"
            self.stdscr.addstr(visible_start + 2, (width - len(msg)) // 2, msg, curses.A_DIM)
            return
        
        # Adjust scroll offset
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + visible_height:
            self.scroll_offset = self.selected_idx - visible_height + 1
        
        # Draw visible notes
        for i in range(visible_height):
            note_idx = i + self.scroll_offset
            if note_idx >= len(notes):
                break
            
            note = notes[note_idx]
            y_pos = visible_start + i
            
            # Determine display attributes
            is_selected = note_idx == self.selected_idx
            is_done = note['done']
            
            if is_selected:
                self.stdscr.attron(curses.color_pair(1))
            elif is_done:
                self.stdscr.attron(curses.color_pair(2))
            else:
                self.stdscr.attron(curses.color_pair(3))
            
            # Format the line
            checkbox = "☑" if is_done else "☐"
            text = note['text']
            max_text_len = width - 8
            if len(text) > max_text_len:
                text = text[:max_text_len-3] + "..."
            
            line = f" {checkbox} {text}"
            line = line.ljust(width - 1)
            
            try:
                self.stdscr.addstr(y_pos, 0, line)
            except curses.error:
                pass
            
            if is_selected:
                self.stdscr.attroff(curses.color_pair(1))
            elif is_done:
                self.stdscr.attroff(curses.color_pair(2))
            else:
                self.stdscr.attroff(curses.color_pair(3))
    
    def draw_footer(self):
        """Draw the footer with help text"""
        height, width = self.stdscr.getmaxyx()
        
        self.stdscr.attron(curses.color_pair(4))
        self.stdscr.addstr(height - 3, 0, "─" * width)
        self.stdscr.attroff(curses.color_pair(4))
        
        if self.input_mode:
            self.stdscr.addstr(height - 2, 2, "New note: " + self.input_buffer + "█")
            self.stdscr.addstr(height - 1, 2, "Enter: Save | Esc: Cancel", curses.A_DIM)
        else:
            help_text = "↑/↓: Navigate | Tab: Switch | Space: Toggle | N: New | D: Delete | Q: Quit"
            if len(help_text) <= width - 4:
                self.stdscr.addstr(height - 2, 2, help_text, curses.A_DIM)
            
            notes = self.get_current_notes()
            count_text = f"Showing {len(notes)} note{'s' if len(notes) != 1 else ''}"
            self.stdscr.addstr(height - 1, 2, count_text, curses.A_DIM)
    
    def draw_input_mode(self):
        """Draw input mode overlay"""
        curses.curs_set(1)  # Show cursor
    
    def handle_input(self):
        """Handle keyboard input"""
        key = self.stdscr.getch()
        
        if key == -1:  # No input
            return True
        
        if self.input_mode:
            if key == 27:  # Escape
                self.input_mode = False
                self.input_buffer = ""
                curses.curs_set(0)
            elif key == 10 or key == curses.KEY_ENTER:  # Enter
                if self.input_buffer.strip():
                    self.nm.add_note(self.input_buffer.strip())
                    self.notes_modified = True
                    self.input_buffer = ""
                self.input_mode = False
                curses.curs_set(0)
                self.selected_idx = 0
                self.scroll_offset = 0
            elif key == curses.KEY_BACKSPACE or key == 127:
                self.input_buffer = self.input_buffer[:-1]
            elif 32 <= key <= 126:  # Printable characters
                self.input_buffer += chr(key)
        else:
            notes = self.get_current_notes()
            
            if key == ord('q') or key == ord('Q'):
                return False
            elif key == curses.KEY_UP or key == ord('k'):
                if notes and self.selected_idx > 0:
                    self.selected_idx -= 1
            elif key == curses.KEY_DOWN or key == ord('j'):
                if notes and self.selected_idx < len(notes) - 1:
                    self.selected_idx += 1
            elif key == 9:  # Tab
                self.current_tab = (self.current_tab + 1) % 3
                self.selected_idx = 0
                self.scroll_offset = 0
            elif key == ord(' '):  # Space - toggle
                if notes:
                    note = notes[self.selected_idx]
                    self.nm.toggle_note(note['id'])
                    self.notes_modified = True
            elif key == ord('n') or key == ord('N'):
                self.input_mode = True
                self.input_buffer = ""
            elif key == ord('d') or key == ord('D'):
                if notes:
                    note = notes[self.selected_idx]
                    self.nm.delete_note(note['id'])
                    self.notes_modified = True
                    if self.selected_idx >= len(self.get_current_notes()):
                        self.selected_idx = max(0, len(self.get_current_notes()) - 1)
        
        return True
    
    def run(self):
        """Main loop"""
        running = True
        last_state = None
        
        try:
            while running:
                # Only redraw if something changed
                current_state = (
                    self.current_tab,
                    self.selected_idx,
                    self.scroll_offset,
                    self.input_mode,
                    self.input_buffer,
                    len(self.get_current_notes())
                )
                
                if current_state != last_state:
                    self.stdscr.erase()  # Use erase() instead of clear()
                    
                    try:
                        self.draw_header()
                        self.draw_notes()
                        self.draw_footer()
                        self.stdscr.refresh()
                        last_state = current_state
                    except KeyboardInterrupt:
                        running = False
                
                running = self.handle_input() and running
        finally:
            # On app close: if internet AND notes were modified, push to Google Tasks
            curses.curs_set(1)  # Show cursor before exit
            self.stdscr.erase()
            self.stdscr.refresh()
            
            if self.has_internet and self.notes_modified:
                # Show syncing message briefly then exit
                self.show_info_message("Syncing changes to Google Tasks...")
                # Run sync in background thread
                sync_thread = threading.Thread(target=self.push_to_google, daemon=False)
                sync_thread.start()
                # Wait for sync to complete (with timeout)
                sync_thread.join(timeout=35)  # Slightly longer than subprocess timeout
            else:
                # No changes or no internet, just close
                if not self.has_internet:
                    self.show_warning_on_close()

def main(stdscr):
    tui = NotesTUI(stdscr)
    tui.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass