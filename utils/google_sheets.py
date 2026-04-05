import os
from pathlib import Path
import gspread
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

def load_env_safely():
    """Locates the .env file in parent directories for flexible deployment."""
    current_path = Path(__file__).resolve()
    for parent in [current_path.parent, current_path.parent.parent, current_path.parent.parent.parent]:
        env_file = parent / '.env'
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            return env_file
    return None

env_path = load_env_safely()

class GoogleSheetsManager:
    def __init__(self):
        # 1. Credentials Setup
        raw_key = os.getenv("GOOGLE_PRIVATE_KEY")
        if not raw_key:
            raise ValueError(f"GOOGLE_PRIVATE_KEY missing. Path: {env_path}")
        
        private_key = raw_key.strip().strip('"').strip("'").replace('\\n', '\n')
        
        service_account_info = {
            "type": "service_account",
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "private_key": private_key,
            "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        try:
            creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
            self.client = gspread.authorize(creds)
            self.sheet_id = os.getenv("GOOGLE_SHEET_ID")
            self.sheet = self.client.open_by_key(self.sheet_id).sheet1
            print(f"[Google Sheets] Initialized successfully.")
        except Exception as e:
            print(f"[Google Sheets] Init Failed: {e}")
            raise

        # 2. Updated Column Mapping (Matching your latest S-column screenshot)
        self.COL_STATUS = 9         # I
        self.COL_LI_TIME = 10       # J
        self.COL_IG_TIME = 11       # K
        self.COL_FB_TIME = 12       # L
        self.COL_MD_TIME = 13       # M
        self.COL_LI_POSTED = 14     # N
        self.COL_IG_POSTED = 15     # O
        self.COL_FB_POSTED = 16     # P
        self.COL_MD_POSTED = 17     # Q
        self.COL_ERROR_LOG = 18     # R
        self.COL_LIVE_LINKS = 19    # S

    def get_draft_tasks(self):
        """Fetch rows marked as 'draft' for AI processing."""
        all_rows = self.sheet.get_all_records()
        return [{'row_index': i + 2, 'data': row} for i, row in enumerate(all_rows) 
                if str(row.get('status', '')).lower().strip() == 'draft']

    def get_approved_tasks(self):
        """Fetch all rows marked as 'approved'. Timing logic is handled in main.py."""
        all_rows = self.sheet.get_all_records()
        return [{'row_index': i + 2, 'data': row} for i, row in enumerate(all_rows) 
                if str(row.get('status', '')).lower().strip() == 'approved']

    def update_ai_content(self, row_index, ig_text, fb_text, md_text):
        """Batch update AI generated content and move to review."""
        # Note: Indexing here matches the column map
        cells = [
            gspread.Cell(row_index, 5, ig_text), # E
            gspread.Cell(row_index, 6, fb_text), # F
            gspread.Cell(row_index, 7, md_text), # G
            gspread.Cell(row_index, self.COL_STATUS, "review")
        ]
        self.sheet.update_cells(cells)

    def update_status(self, row_index, new_status):
        """Update the status cell (e.g., to 'published')."""
        try:
            self.sheet.update_cell(row_index, self.COL_STATUS, new_status)
        except Exception as e:
            print(f"[Sheets] Status update failed: {e}")

    def mark_posted(self, row_index, platform_code):
        """Updates the specific platform posted column to 'Yes'."""
        col_map = {
            'LI': self.COL_LI_POSTED,
            'IG': self.COL_IG_POSTED,
            'FB': self.COL_FB_POSTED,
            'MD': self.COL_MD_POSTED
        }
        col = col_map.get(platform_code)
        if col:
            try:
                self.sheet.update_cell(row_index, col, "Yes")
            except Exception as e:
                print(f"[Sheets] Failed to mark {platform_code} as posted: {e}")

    def log_event(self, row_index, error=None, link=None):
        """Logs errors to Col R or success links to Col S."""
        try:
            if error:
                self.sheet.update_cell(row_index, self.COL_ERROR_LOG, str(error))
            
            if link:
                # Get existing links to append
                cell_data = self.sheet.cell(row_index, self.COL_LIVE_LINKS).value
                existing = str(cell_data) if cell_data else ""
                new_val = f"{existing}\n{link}".strip() if existing else str(link)
                self.sheet.update_cell(row_index, self.COL_LIVE_LINKS, new_val)
        except Exception as e:
            print(f"[Sheets] Logging failed for row {row_index}: {e}")

if __name__ == "__main__":
    mgr = GoogleSheetsManager()
    print("Connection Test Successful.")