import os
import requests
from dotenv import load_dotenv

load_dotenv()

def post_to_linkedin(text, image_path=None):
    """
    LinkedIn API V202602: Register -> Upload -> Create Post.
    """
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    person_urn = os.getenv("LINKEDIN_PERSON_URN")
    
    if not access_token or not person_urn:
        return False, "Missing Credentials"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": "202602",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    image_asset_id = None

    # --- STEP 1: Handle Image Binary Upload ---
    if image_path and os.path.exists(image_path):
        try:
            # 1.1 Register Image
            register_url = "https://api.linkedin.com/rest/images?action=initializeUpload"
            register_data = {"initializeUploadRequest": {"owner": person_urn}}
            reg_res = requests.post(register_url, headers=headers, json=register_data, timeout=20)
            
            if reg_res.status_code == 200:
                reg_data = reg_res.json()['value']
                upload_url = reg_data['uploadUrl']
                image_asset_id = reg_data['image']
                
                # 1.2 Upload Binary
                with open(image_path, 'rb') as f:
                    binary_headers = {"Authorization": f"Bearer {access_token}"}
                    upload_res = requests.put(upload_url, headers=binary_headers, data=f, timeout=30)
                
                if upload_res.status_code != 201:
                    image_asset_id = None
        except Exception as e:
            print(f"LI Image Error: {e}")

    # --- STEP 2: Create Post ---
    post_url = "https://api.linkedin.com/rest/posts"
    post_data = {
        "author": person_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "lifecycleState": "PUBLISHED",
        "distribution": {"feedDistribution": "MAIN_FEED"}
    }

    if image_asset_id:
        post_data["content"] = {"media": {"title": "Post Image", "id": image_asset_id}}

    try:
        response = requests.post(post_url, headers={**headers, "Content-Type": "application/json"}, json=post_data, timeout=30)
        if response.status_code == 201:
            return True, response.headers.get('x-restli-id', 'Success')
        return False, response.text
    except Exception as e:
        return False, str(e)