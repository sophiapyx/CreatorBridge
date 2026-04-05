import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# --- 1. SECURE PATH LOCATOR ---
current_file = Path(__file__).resolve()
env_path = next((p / '.env' for p in [current_file.parent, current_file.parent.parent] if (p / '.env').exists()), None)

if env_path:
    load_dotenv(dotenv_path=env_path)
    print(f"Environment loaded from: {env_path}")
else:
    print(" Error: .env file not found.")
    exit(1)

def publish_official_post():
    """
    Publishes a custom image and a professional caption to Instagram.
    """
    print("\n" + "="*50)
    print(" IG OFFICIAL RELEASE: CreatorBridge")
    print("="*50)

    # Fetch from .env
    ig_user_id = os.getenv("IG_USER_ID")
    access_token = os.getenv("IG_ACCESS_TOKEN")
    
    # --- CUSTOM CONTENT ---
    # picture (from Unsplash)
    IMAGE_URL = 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1200&q=80'
    
    # content
    CAPTION = (
        "Hello World! 🚀\n\n"
        "Excited to announce that my automated social media system 'CreatorBridge' is now LIVE. "
        "Built with Python and Meta Graph API, this tool streamlines cross-platform content delivery. "
        "Stay tuned for more updates! \n\n"
        "#Python #Automation #CreatorBridge #MetaAPI #SoftwareDevelopment"
    )

    if not ig_user_id or not access_token:
        print("Error: Credentials missing in .env")
        return

    # --- STEP 1: Create Media Container ---
    print(f"Step 1: Uploading official media to Instagram...")
    url_1 = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
    payload_1 = {
        'image_url': IMAGE_URL,
        'caption': CAPTION,
        'access_token': access_token
    }
    
    res_1 = requests.post(url_1, data=payload_1).json()
    
    if 'id' in res_1:
        creation_id = res_1['id']
        print(f"Container created! ID: {creation_id}")
        
        # --- WAIT FOR META PROCESSING ---
        print("Waiting 10 seconds for Instagram to process the high-res image...")
        time.sleep(10)
        
        # --- STEP 2: Final Publish ---
        print(f"🎬 Step 2: Finalizing the official post...")
        url_2 = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
        payload_2 = {
            'creation_id': creation_id,
            'access_token': access_token
        }
        
        res_2 = requests.post(url_2, data=payload_2).json()
        
        if 'id' in res_2:
            print("-" * 50)
            print("🎊 MISSION ACCOMPLISHED!")
            print("Your official CreatorBridge post is now LIVE on Instagram.")
            print(f"Post ID: {res_2['id']}")
        else:
            print(f"Step 2 Failed: {res_2}")
    else:
        print(f"Step 1 Failed: {res_1}")

if __name__ == "__main__":
    publish_official_post()