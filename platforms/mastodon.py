import os
import requests
from dotenv import load_dotenv

load_dotenv()

def post_to_mastodon(text, image_path=None):
    """
    Publishes content to Mastodon based on your successful test code.
    Returns: (bool, info)
    """
    access_token = os.getenv("MASTODON_ACCESS_TOKEN")
    instance_url = os.getenv("MASTODON_INSTANCE") # e.g., https://mastodon.social
    
    if not access_token or not instance_url:
        return False, "Missing Mastodon credentials in .env"

    headers = {"Authorization": f"Bearer {access_token}"}
    media_ids = []

    # --- STEP 1: Upload Media (Exactly as your test) ---
    if image_path and os.path.exists(image_path):
        try:
            with open(image_path, 'rb') as file:
                files = {'file': file}
                # Note: Mastodon API endpoint for media
                media_res = requests.post(
                    f"{instance_url}/api/v1/media",
                    headers=headers,
                    files=files,
                    timeout=30
                )
            
            if media_res.status_code == 200:
                media_id = media_res.json().get('id')
                media_ids.append(media_id)
            else:
                return False, f"Media Upload Failed: {media_res.text}"
        except Exception as e:
            return False, f"Media Upload Exception: {str(e)}"

    # --- STEP 2: Post Status (Exactly as your test) ---
    status_url = f"{instance_url}/api/v1/statuses"
    payload = {
        "status": text,
        "visibility": "public"
    }
    
    if media_ids:
        # Note the 'media_ids[]' key format required by Mastodon API
        payload["media_ids[]"] = media_ids

    try:
        response = requests.post(status_url, headers=headers, data=payload, timeout=30)
        
        if response.status_code == 200:
            res_data = response.json()
            # Return the live URL of the post for your Google Sheet
            return True, res_data.get('url', 'Success')
        else:
            return False, f"Status Post Failed ({response.status_code}): {response.text}"
            
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

if __name__ == "__main__":
    # Test function
    success, info = post_to_mastodon("Unit test from platforms layer!")
    print(f"Result: {success}, Info: {info}")