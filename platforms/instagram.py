import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def post_to_instagram(text, image_url):
    """
    Instagram 'Arm' - Only executes the post.
    """
    ig_user_id = os.getenv("IG_USER_ID")
    access_token = os.getenv("IG_ACCESS_TOKEN")
    base_url = "https://graph.facebook.com/v19.0"
    
    if not ig_user_id or not access_token:
        return False, "Missing IG Credentials"

    try:
        # STEP 1: Create Media Container
        container_url = f"{base_url}/{ig_user_id}/media"
        payload = {
            'image_url': image_url,
            'caption': text,
            'access_token': access_token
        }
        
        res_1 = requests.post(container_url, params=payload).json()
        
        if 'id' in res_1:
            creation_id = res_1['id']
            print(f"[Instagram] Container {creation_id} created. Waiting 15s...")
            time.sleep(15) 
            
            # STEP 2: Final Publish
            publish_url = f"{base_url}/{ig_user_id}/media_publish"
            res_2 = requests.post(publish_url, params={'creation_id': creation_id, 'access_token': access_token}).json()
            
            if 'id' in res_2:
                return True, f"IG Post ID: {res_2['id']}"
            return False, f"Publishing Failed: {res_2}"
        
        return False, f"Container Failed: {res_1}"

    except Exception as e:
        return False, str(e)