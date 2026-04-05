import os
import requests
from dotenv import load_dotenv

# 1. Load configuration
load_dotenv()

def post_to_mastodon():
    # Fetch credentials from .env
    access_token = os.getenv("MASTODON_ACCESS_TOKEN")
    instance_url = os.getenv("MASTODON_INSTANCE") # e.g., https://mastodon.social
    
    # Path to your test image
    # Update this path to an actual image file on your Mac mini
    image_path = "/Users/apple/Documents/Work/Social_media_automation/test_image.jpg"

    if not access_token or not instance_url:
        print(" Error: Missing MASTODON_ACCESS_TOKEN or MASTODON_INSTANCE in .env")
        return

    headers = {"Authorization": f"Bearer {access_token}"}

    # STEP 1: Upload Media
    media_id = None
    if os.path.exists(image_path):
        print(f" Uploading image: {image_path}...")
        try:
            with open(image_path, 'rb') as file:
                media_data = {'file': file}
                media_res = requests.post(
                    f"{instance_url}/api/v1/media",
                    headers=headers,
                    files=media_data
                )
            
            if media_res.status_code == 200:
                media_id = media_res.json().get('id')
                print(f" Media uploaded! ID: {media_id}")
            else:
                print(f" Media upload failed: {media_res.text}")
        except Exception as e:
            print(f" Error during media upload: {e}")
    else:
        print(" No image found at path, proceeding with text-only post.")

    # STEP 2: Post Status
    print(" Sending status to Mastodon...")
    status_url = f"{instance_url}/api/v1/statuses"
    
    payload = {
        "status": "Final integration test for CreatorBridge! This post includes automated text and media verification. #SIAT #Automation #OpenSource",
        "visibility": "public"
    }
    
    if media_id:
        payload["media_ids[]"] = [media_id]

    try:
        response = requests.post(status_url, headers=headers, data=payload)
        
        if response.status_code == 200:
            print(" Success! Your Mastodon post is live.")
        else:
            print(f" Failed! Status Code: {response.status_code}")
            print(f"Error Details: {response.text}")
            
    except Exception as e:
        print(f" An unexpected error occurred: {e}")

if __name__ == "__main__":
    post_to_mastodon()