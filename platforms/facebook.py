import os
import requests
from dotenv import load_dotenv

load_dotenv()

def post_to_facebook(text, image_url):
    """
    Facebook 'Arm' - Uses Page Photos API to post with a URL.
    Optimized for 1:1 square images to minimize black borders.
    """
    page_id = os.getenv("FB_PAGE_ID")
    page_token = os.getenv("FB_ACCESS_TOKEN")
    
    if not page_id or not page_token:
        return False, "Missing FB_PAGE_ID or FB_ACCESS_TOKEN"

    # Using the /photos endpoint is the best way to reduce borders for 1:1 images
    url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
    
    payload = {
        'caption': text,
        'access_token': page_token,
        'published': 'true'
    }

    if image_url:
        # Posting as a photo object
        payload['url'] = image_url
    else:
        # Fallback to feed for text-only posts
        url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
        payload = {'message': text, 'access_token': page_token}

    try:
        response = requests.post(url, data=payload, timeout=30)
        res_data = response.json()
        
        if 'id' in res_data:
            # Return only the ID; main.py handles the URL formatting
            return True, res_data['id']
        else:
            return False, f"FB Error: {res_data.get('error', {}).get('message', res_data)}"
    except Exception as e:
        return False, f"FB Connection Error: {str(e)}"