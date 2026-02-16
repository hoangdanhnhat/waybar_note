#!/home/ratatoui1e/programing/waybar_note/.venv/bin/python
"""
Google Tasks Sync - Sync notes with Google Tasks
"""
import json
import os
import pickle
from pathlib import Path
from datetime import datetime, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import sys
sys.path.insert(0, str(Path(__file__).parent))
from notes_manager import NotesManager

# If modifying these scopes, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/tasks']

CONFIG_DIR = Path.home() / ".config" / "waybar-notes"
TOKEN_FILE = CONFIG_DIR / "token.pickle"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
SYNC_STATE_FILE = CONFIG_DIR / "sync_state.json"

class GoogleTasksSync:
    def __init__(self):
        self.nm = NotesManager()
        self.service = None
        self.sync_state = self.load_sync_state()
    
    def load_sync_state(self):
        """Load sync state (mapping between local IDs and Google Task IDs)"""
        if SYNC_STATE_FILE.exists():
            try:
                with open(SYNC_STATE_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"mapping": {}, "last_sync": None}
        return {"mapping": {}, "last_sync": None}
    
    def save_sync_state(self):
        """Save sync state"""
        with open(SYNC_STATE_FILE, 'w') as f:
            json.dump(self.sync_state, f, indent=2)
    
    def authenticate(self):
        """Authenticate with Google Tasks API"""
        creds = None
        
        # Load existing credentials
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing access token...")
                creds.refresh(Request())
            else:
                if not CREDENTIALS_FILE.exists():
                    print(f"\n❌ Error: credentials.json not found!")
                    print(f"Please download OAuth2 credentials from Google Cloud Console")
                    print(f"and save them to: {CREDENTIALS_FILE}")
                    print("\nSee setup instructions in README.md")
                    return False
                
                print("Opening browser for authentication...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('tasks', 'v1', credentials=creds)
        return True
    
    def get_all_task_lists(self):
        """Get all task lists"""
        try:
            results = self.service.tasklists().list().execute()
            task_lists = results.get('items', [])
            print(f"✓ Found {len(task_lists)} task list(s)")
            return task_lists
        except HttpError as error:
            print(f"❌ Error accessing task lists: {error}")
            return []
    
    def sync_to_google(self):
        """Push local notes to Google Tasks"""
        print("\n📤 Syncing to Google Tasks...")
        
        # Get all task lists
        task_lists = self.get_all_task_lists()
        if not task_lists:
            print("❌ No task lists found")
            return
        
        # Use the first task list (default) for new tasks
        default_list_id = task_lists[0]['id']
        default_list_name = task_lists[0]['title']
        
        local_notes = self.nm.get_all_notes()
        
        for note in local_notes:
            local_id = str(note['id'])
            
            # Check if note already exists in Google
            if local_id in self.sync_state['mapping']:
                # Update existing task
                mapping = self.sync_state['mapping'][local_id]
                google_id = mapping['task_id']
                list_id = mapping['list_id']
                self.update_google_task(list_id, google_id, note)
            else:
                # Create new task in default list
                google_id = self.create_google_task(default_list_id, note)
                if google_id:
                    self.sync_state['mapping'][local_id] = {
                        'task_id': google_id,
                        'list_id': default_list_id,
                        'list_name': default_list_name
                    }
        
        self.sync_state['last_sync'] = datetime.now(timezone.utc).isoformat()
        self.save_sync_state()
        print("✓ Sync to Google complete")
    
    def sync_from_google(self):
        """Pull tasks from all Google Task lists and update local notes"""
        print("\n📥 Syncing from Google Tasks...")
        
        # Get all task lists
        task_lists = self.get_all_task_lists()
        if not task_lists:
            print("❌ No task lists found")
            return
        
        # Create reverse mapping (google_id -> local_id)
        reverse_mapping = {}
        for local_id, mapping in self.sync_state['mapping'].items():
            if isinstance(mapping, dict):
                reverse_mapping[mapping['task_id']] = local_id
            else:
                # Old format compatibility
                reverse_mapping[mapping] = local_id
        
        # Process all task lists
        for task_list in task_lists:
            list_id = task_list['id']
            list_name = task_list['title']
            
            try:
                # Get all tasks from this list
                results = self.service.tasks().list(
                    tasklist=list_id,
                    showCompleted=True,
                    showHidden=True
                ).execute()
                
                google_tasks = results.get('items', [])
                print(f"  Processing '{list_name}': {len(google_tasks)} task(s)")
                
                for gtask in google_tasks:
                    google_id = gtask['id']
                    
                    if google_id in reverse_mapping:
                        # Update existing local note
                        local_id = int(reverse_mapping[google_id])
                        self.update_local_note(local_id, gtask)
                    else:
                        # Create new local note
                        local_note = self.create_local_note(gtask)
                        if local_note:
                            self.sync_state['mapping'][str(local_note['id'])] = {
                                'task_id': google_id,
                                'list_id': list_id,
                                'list_name': list_name
                            }
                
            except HttpError as error:
                print(f"  ❌ Error syncing from list '{list_name}': {error}")
        
        self.sync_state['last_sync'] = datetime.now(timezone.utc).isoformat()
        self.save_sync_state()
        print("✓ Sync from Google complete")
    
    def create_google_task(self, list_id, note):
        """Create a new task in Google Tasks"""
        try:
            task_body = {
                'title': note['text'],
                'status': 'completed' if note['done'] else 'needsAction'
            }
            
            result = self.service.tasks().insert(
                tasklist=list_id,
                body=task_body
            ).execute()
            
            print(f"  ✓ Created: {note['text'][:50]}")
            return result['id']
            
        except HttpError as error:
            print(f"  ❌ Error creating task: {error}")
            return None
    
    def update_google_task(self, list_id, google_id, note):
        """Update existing Google Task"""
        try:
            task_body = {
                'id': google_id,
                'title': note['text'],
                'status': 'completed' if note['done'] else 'needsAction'
            }
            
            self.service.tasks().update(
                tasklist=list_id,
                task=google_id,
                body=task_body
            ).execute()
            
            print(f"  ✓ Updated: {note['text'][:50]}")
            
        except HttpError as error:
            print(f"  ❌ Error updating task: {error}")
    
    def create_local_note(self, gtask):
        """Create a new local note from Google Task"""
        note = self.nm.add_note(gtask['title'])
        
        # Update status if completed
        if gtask.get('status') == 'completed':
            note['done'] = True
            note['completed'] = gtask.get('completed', datetime.now(timezone.utc).isoformat())
            self.nm.save_notes()
        
        print(f"  ✓ Created locally: {gtask['title'][:50]}")
        return note
    
    def update_local_note(self, local_id, gtask):
        """Update existing local note from Google Task"""
        for note in self.nm.notes:
            if note['id'] == local_id:
                note['text'] = gtask['title']
                note['done'] = gtask.get('status') == 'completed'
                if note['done']:
                    note['completed'] = gtask.get('completed', datetime.now(timezone.utc).isoformat())
                else:
                    note['completed'] = None
                
                self.nm.save_notes()
                print(f"  ✓ Updated locally: {gtask['title'][:50]}")
                break
    
    def bidirectional_sync(self):
        """Perform full bidirectional sync"""
        print("\n🔄 Starting bidirectional sync...")
        
        # First push local changes to Google (local changes take priority)
        self.sync_to_google()
        
        # Then pull changes from Google (to get any changes made in Google)
        self.sync_from_google()
        
        print("\n✅ Sync complete!")
        print(f"Last synced: {self.sync_state.get('last_sync', 'Never')}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync notes with Google Tasks')
    parser.add_argument('--setup', action='store_true', help='Setup Google Tasks authentication')
    parser.add_argument('--sync', action='store_true', help='Perform bidirectional sync')
    parser.add_argument('--pull', action='store_true', help='Pull from Google Tasks only')
    parser.add_argument('--push', action='store_true', help='Push to Google Tasks only')
    
    args = parser.parse_args()
    
    sync = GoogleTasksSync()
    
    # Authenticate
    if not sync.authenticate():
        return 1
    
    # Get all task lists
    task_lists = sync.get_all_task_lists()
    if not task_lists:
        print("❌ No task lists found. Create at least one task list in Google Tasks first.")
        return 1
    
    # Perform requested action
    if args.pull:
        sync.sync_from_google()
    elif args.push:
        sync.sync_to_google()
    elif args.sync or args.setup:
        sync.bidirectional_sync()
    else:
        # Default: show status
        print("\n📊 Sync Status")
        print(f"Task lists: {len(task_lists)}")
        for tl in task_lists:
            print(f"  • {tl['title']}")
        print(f"Synced notes: {len(sync.sync_state['mapping'])}")
        print(f"Last sync: {sync.sync_state.get('last_sync', 'Never')}")
        print("\nUse --sync to synchronize now")

if __name__ == "__main__":
    exit(main() or 0)