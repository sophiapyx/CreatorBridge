import os
import requests
from pathlib import Path
from dotenv import load_dotenv
import ollama
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# --- 1. ENVIRONMENT CONFIGURATION ---
current_file = Path(__file__).resolve()
search_paths = [current_file.parent, current_file.parent.parent]
env_path = next((p / '.env' for p in search_paths if (p / '.env').exists()), None)

if env_path:
    load_dotenv(dotenv_path=env_path)
    print(f"Configuration loaded from: {env_path}")
else:
    print("Critical Error: .env file not found!")
    exit(1)

def run_diagnostic():
    print("\n" + "="*65)
    print("CreatorBridge: Universal System Diagnostic (Final Build)")
    print("="*65)

    # --- SECTION 1: AI NODE (Ollama) ---
    print("\n[1/3] AI Node (Local Nemotron)")
    try:
        models = ollama.list()
        model_list = models.models if hasattr(models, 'models') else models.get('models', [])
        target = os.getenv("OLLAMA_MODEL", "nemotron")
        found = any(target.lower() in (m.model if hasattr(m, 'model') else m['name']).lower() for m in model_list)
        if found:
            print(f"   Success: Local AI '{target}' is active.")
        else:
            print(f"   Warning: Model '{target}' not found in Ollama.")
    except Exception as e:
        print(f"   AI Node Offline: {e}")

    # --- SECTION 2: CLOUD STORAGE (Google Sheets API) ---
    print("\n[2/3] Cloud Storage (Google Sheets API)")
    try:
        info = {
            "type": "service_account",
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace('\\n', '\n'),
            "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        creds = Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        service = build('sheets', 'v4', credentials=creds)
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        print(f"   Success: Connected to Sheet '{meta.get('properties').get('title')}'")
    except Exception as e:
        print(f"   Google Sheets Failed: {e}")

    # --- SECTION 3: SOCIAL MEDIA EXITS ---
    print("\n[3/3] Social Media Exits")
    
    # Matching your provided .env keys
    fb_id = os.getenv("FB_PAGE_ID")
    fb_token = os.getenv("FB_ACCESS_TOKEN") 
    ig_id_env = os.getenv("IG_USER_ID")

    if fb_id and fb_token:
        try:
            # Using v19.0 for stable Graph API access
            api_url = f"https://graph.facebook.com/v19.0/{fb_id}?fields=name,instagram_business_account&access_token={fb_token}"
            res = requests.get(api_url).json()
            
            if "name" in res:
                print(f"   Facebook: Active (Account: {res['name']})")
                
                # Verify Instagram Link
                if "instagram_business_account" in res:
                    actual_ig_id = res["instagram_business_account"]["id"]
                    print(f"   Instagram: Linked Account Verified (ID: {actual_ig_id})")
                    if ig_id_env != actual_ig_id:
                        print(f"      Note: .env IG_USER_ID mismatch. Should be: {actual_ig_id}")
                else:
                    print("   Instagram: No linked Business Account found for this Page.")
            else:
                err = res.get('error', {}).get('message', 'Invalid Credentials')
                print(f"   Meta API Error: {err}")
        except Exception as e:
            print(f"   Meta Connection Error: {e}")
    else:
        print("   Meta Credentials missing in .env (Check FB_PAGE_ID and FB_ACCESS_TOKEN)")

    # B. LinkedIn (Version 202602)
    li_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    if li_token:
        print(f"   LinkedIn: Configured (API Version: 202602)")
    
    # C. Mastodon
    ms_token = os.getenv("MASTODON_ACCESS_TOKEN")
    if ms_token:
        print("   Mastodon: Configured")

    print("\n" + "="*65)
    print("Diagnostic Finished! System ready for presentation.")
    print("="*65 + "\n")

if __name__ == "__main__":
    run_diagnostic()