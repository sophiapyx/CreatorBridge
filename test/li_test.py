import os
import requests
from dotenv import load_dotenv

# 1.  .env 
load_dotenv()

def test_linkedin_final():
  
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    person_urn = os.getenv("LINKEDIN_PERSON_URN")
    
    if not access_token or not person_urn:
        print(" Error: Missing LINKEDIN_ACCESS_TOKEN or LINKEDIN_PERSON_URN in .env")
        return

    # 2. LinkedIn API 
    url = "https://api.linkedin.com/rest/posts"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": "202602",  
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    # 3. content
    post_data = {
        "author": person_urn,
        "commentary": "Final test for CreatorBridge project! 🚀 This automated post marks the successful integration of LinkedIn API. #SIAT #IAT460 #Automation",
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }

    print(" Sending final post to LinkedIn...")
    
    try:
        response = requests.post(url, headers=headers, json=post_data)
        
        if response.status_code == 201:
            print(" Success! Your LinkedIn post is live.")
            print(f"Response: {response.status_code}")
        elif response.status_code == 426:
            print(" Version Error: LinkedIn updated their API version again.")
            print(" Tip: Try changing 'LinkedIn-Version' to '202603' in the code.")
        else:
            print(f" Failed! Status Code: {response.status_code}")
            print(f"Error Details: {response.text}")
            
    except Exception as e:
        print(f" An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_linkedin_final()