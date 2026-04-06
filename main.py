import os
import time
import re
import requests
import pytz  
from datetime import datetime
from utils.google_sheets import GoogleSheetsManager
from utils.ai_agent import AIAgent
from platforms.linkedin import post_to_linkedin
from platforms.instagram import post_to_instagram
from platforms.facebook import post_to_facebook
from platforms.mastodon import post_to_mastodon

def get_clean_url(url):
    """ Cleans URLs for Meta API while keeping Discord tokens valid. """
    if not url: return None
    url = str(url).strip()
    if "drive.google.com" in url:
        match = re.search(r'(?:/d/|id=)([a-zA-Z0-9_-]+)', url)
        return f"https://drive.google.com/uc?export=download&id={match.group(1)}" if match else url
    if "discordapp" in url:
        if "format=webp" in url:
            url = url.replace("format=webp", "format=jpg")
        return url
    return url

def check_timing(scheduled_val):
    """
    Returns True if the content should be posted now.
    Comparing against Vancouver (Pacific) time for GitHub Actions compatibility.
    """
    val = str(scheduled_val).strip().upper()
    if not val:
        return False
    
    if val == "NOW":
        return True
    
    try:
        vancouver_tz = pytz.timezone('America/Vancouver')
        now_vancouver = datetime.now(vancouver_tz).replace(tzinfo=None)
        
        # Supports both YYYY-MM-DD HH:MM:SS and YYYY-MM-DD HH:MM
        fmt = '%Y-%m-%d %H:%M:%S' if len(val) > 16 else '%Y-%m-%d %H:%M'
        scheduled_time = datetime.strptime(val, fmt)
        
        return now_vancouver >= scheduled_time
    except ValueError:
        return False

def main():
    sheet_mgr = GoogleSheetsManager()
    ai_agent = AIAgent()
    
    vancouver_tz = pytz.timezone('America/Vancouver')
    now_str = datetime.now(vancouver_tz).strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n CreatorBridge Orchestrator Start (Vancouver Time): {now_str}")

    # --- TASK 1: AI Content Generation ---
    drafts = sheet_mgr.get_draft_tasks()
    if drafts:
        for task in drafts:
            idx = task['row_index']
            row_data = task['data']
            li_text = row_data.get('LI_CONTENT', '')
            exist_ig = str(row_data.get('AI_IG', '')).strip()
            exist_fb = str(row_data.get('AI_FB', '')).strip()
            exist_md = str(row_data.get('AI_MD', '')).strip()

            if li_text:
                if not exist_ig or not exist_fb or not exist_md:
                    print(f"Row {idx}: Filling AI content gaps...")
                    try:
                        ai_results = ai_agent.generate_posts(li_text)
                        final_ig = exist_ig if exist_ig else ai_results['ig']
                        final_fb = exist_fb if exist_fb else ai_results['fb']
                        final_md = exist_md if exist_md else ai_results['md']
                        sheet_mgr.update_ai_content(idx, final_ig, final_fb, final_md)
                        sheet_mgr.sheet.update_cell(idx, sheet_mgr.COL_STATUS, "review")
                    except Exception as e:
                        print(f" AI Error Row {idx}: {e}")
                else:
                    sheet_mgr.sheet.update_cell(idx, sheet_mgr.COL_STATUS, "review")

    # --- TASK 2: Distribution (Smart Scheduling) ---
    approved_tasks = sheet_mgr.get_approved_tasks() 
    if not approved_tasks:
        print("No approved tasks ready for processing.")
        return

    for task in approved_tasks:
        idx = task['row_index']
        row = task['data']
        
        platform_map = [
            ('LI', post_to_linkedin, 'LI_posted', 'LI_time', 'LI_CONTENT'),
            ('IG', post_to_instagram, 'IG_posted', 'IG_time', 'AI_IG'),
            ('FB', post_to_facebook, 'FB_posted', 'FB_time', 'AI_FB'),
            ('MD', post_to_mastodon, 'MD_posted', 'MD_time', 'AI_MD')
        ]

        direct_url = get_clean_url(row.get('media_url', ''))
        local_path = None
        row_all_done = True 

        for code, func, post_key, time_key, content_key in platform_map:
            is_posted = str(row.get(post_key, 'No')).strip().lower() == 'yes'
            scheduled_val = row.get(time_key, '')
            content = row.get(content_key, '')

            if not is_posted and scheduled_val and content:
                if check_timing(scheduled_val):
                    print(f"\n[Row {idx}] Triggering {code} release...")
                    
                    if not local_path and direct_url:
                        try:
                            res = requests.get(direct_url, timeout=20)
                            if res.status_code == 200:
                                local_path = os.path.abspath(f"temp_{idx}.jpg")
                                with open(local_path, 'wb') as f: f.write(res.content)
                        except: pass

                    img_arg = direct_url if code in ['IG', 'FB'] else local_path
                    success, info = func(content, img_arg)

                    if success:
                        formatted_link = info
                        if code == 'LI' and not str(info).startswith('http'):
                            formatted_link = f"https://www.linkedin.com/feed/update/{info}"
                        elif code == 'FB' and not str(info).startswith('http'):
                            formatted_link = f"https://www.facebook.com/{info}"
                        elif code == 'IG' and not str(info).startswith('http'):
                            formatted_link = f"https://www.instagram.com/sophiapeng39/"
                        
                        sheet_mgr.mark_posted(idx, code)
                        sheet_mgr.log_event(idx, link=f"{code}: {formatted_link}")
                        print(f" {code}: Post Successful. URL: {formatted_link}")
                    else:
                        sheet_mgr.log_event(idx, error=f"{code} Fail: {info}")
                        print(f" {code}: Post Failed. Error Detail: {info}")
                        row_all_done = False
                else:
                    row_all_done = False
            elif not is_posted and not scheduled_val:
                pass
            elif not is_posted:
                row_all_done = False

        if row_all_done:
            print(f"Row {idx}: All platforms published. Updating status to 'published'.")
            sheet_mgr.sheet.update_cell(idx, sheet_mgr.COL_STATUS, "published")

        if local_path and os.path.exists(local_path):
            os.remove(local_path)

if __name__ == "__main__":
    main()