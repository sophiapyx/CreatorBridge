import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# 1. Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def publish_to_facebook():
    print("\n" + "="*50)
    print(" FB OFFICIAL RELEASE: CreatorBridge")
    print("="*50)

    # Fetch credentials
    page_id = os.getenv("FB_PAGE_ID")
    access_token = os.getenv("FB_ACCESS_TOKEN")
    
    if not page_id or not access_token:
        print(" Error: Missing FB_PAGE_ID or FB_ACCESS_TOKEN in .env")
        return

    # Use the correct Page Feed endpoint
    # Note: v19.0 or v21.0 are both stable for 2026 workflows
    url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    
    # Final production message
    payload = {
        "message": "Final integration test for CreatorBridge! This post verifies the connection between Google Sheets and Facebook Graph API. #SIAT #Automation #CreatorBridge",
        "access_token": access_token
    }

    print(f" Sending official post to Sophia Studio (ID: {page_id})...")
    
    try:
        response = requests.post(url, data=payload)
        result = response.json()

        if response.status_code == 200 and "id" in result:
            print(f" Success! Post live on Facebook.")
            print(f" Post ID: {result['id']}")
            print(f" View at: https://www.facebook.com/{result['id']}")
        else:
            print(f" FB Publishing Failed: {result}")
            if "publish_actions" in str(result):
                print("\n Critical Tip: Do NOT use 'publish_actions'.")
                print("   Make sure your Token is a PAGE TOKEN from 'me/accounts' with 'pages_manage_posts'.")
                
    except Exception as e:
        print(f" An unexpected error occurred: {e}")

if __name__ == "__main__":
    publish_to_facebook()