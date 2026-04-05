import os
import time  
import requests
import json 
from pathlib import Path
from dotenv import load_dotenv

# --- SMART PATH LOCATOR ---
def load_env_safely():
    current_path = Path(__file__).resolve()
    for parent in [current_path.parent, current_path.parent.parent, current_path.parent.parent.parent]:
        env_file = parent / '.env'
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            return env_file
    return None

load_env_safely()

class AIAgent:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        # If the .env file is not read, the default version will be llama3.1.
        self.model = os.getenv("OLLAMA_MODEL", "llama3.1")
        self.endpoint = f"{self.base_url}/api/generate"

    def _call_ai(self, prompt):
        # Increase the num_ctx (context window) limit
        payload = {
            "model": self.model, 
            "prompt": prompt, 
            "stream": False,
            "options": {
                "num_ctx": 4096,
                "temperature": 0.7
            }
        }
        try:
            res = requests.post(self.endpoint, json=payload, timeout=180)
            res.raise_for_status()
            return res.json().get('response', '').strip()
        except Exception as e:
            # Return the specific error so that main.py can capture it.
            raise Exception(f"Ollama Error ({self.model}): {str(e)}")

    def generate_posts(self, li_content):
        # Optimized prompt: Llama 3.1 prefers clear structure
        hashtag_instruction = "Identify all original #hashtags. Keep them exactly as they are. Place them at the very end."

        # 1. Instagram Prompt (Optimization: Clearly prohibit the output of links)
        prompt_ig = (
            f"Task: Rewrite for Instagram.\n"
            f"Content: {li_content}\n\n"
            f"Strict Rules:\n"
            f"1. Max 1000 chars.\n"
            f"2. REMOVE all URLs. Replace with: 'Check the link in bio!'\n"
            f"3. {hashtag_instruction}\n"
            f"4. Use vibrant tone and emojis."
        )

        # 2. Facebook Prompt
        prompt_fb = (
            f"Task: Rewrite for Facebook.\n"
            f"Content: {li_content}\n\n"
            f"Strict Rules:\n"
            f"1. Max 3000 chars.\n"
            f"2. KEEP all links and 🔗 symbols.\n"
            f"3. {hashtag_instruction}\n"
            f"4. Use a friendly, community-oriented tone."
        )

        # 3. Mastodon Prompt 
        prompt_md = (
            f"Task: Rewrite for Mastodon.\n"
            f"Content: {li_content}\n\n"
            f"Strict Rules:\n"
            f"1. STRICT LIMIT: 400 CHARACTERS TOTAL.\n"
            f"2. Keep links.\n"
            f"3. {hashtag_instruction}\n"
            f"4. Concise and tech-focused. Summarize if necessary."
        )

        results = {}
        # Increase the interval time
        print(f"[AI Agent] Generating IG...")
        results["ig"] = self._call_ai(prompt_ig)
        time.sleep(2) 

        print(f"[AI Agent] Generating FB...")
        results["fb"] = self._call_ai(prompt_fb)
        time.sleep(2)

        print(f"[AI Agent] Generating MD...")
        results["md"] = self._call_ai(prompt_md)

        return results

if __name__ == "__main__":
    agent = AIAgent()
    print(f"AI Agent ready. Using model: {agent.model}")