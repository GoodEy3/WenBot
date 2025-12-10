import os
import sys
import time
import logging
import random
import requests
import sqlite3
import asyncio
from datetime import datetime
import json
from dotenv import load_dotenv

# Load secrets
load_dotenv()

# --- LOGGING SETUP ---
# Fixed the "handlers=" syntax error
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(module)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("StakeDominator")

# --- DISCORD ALERT FUNCTION ---
def send_discord_alert(message_content):
    """
    Sends a message to the Discord channel via Webhook.
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        logger.error("❌ Error: No Discord Webhook URL found in .env")
        return

    data = {
        "content": message_content,
        "username": "WenBot 🤖"
    }

    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 204:
            logger.info("✅ Discord message sent successfully!")
        else:
            logger.warning(f"⚠️ Failed to send Discord message. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error sending to Discord: {e}")

# --- INFRASTRUCTURE IMPORTS ---
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

# --- MEDIA & SEO IMPORTS ---
try:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
except ImportError:
    logger.warning("MoviePy not installed. Video features will be disabled.")

try:
    import praw
except ImportError:
    logger.warning("PRAW not installed. Reddit features will be disabled.")

# --- GLOBAL CONFIGURATION ---
REF_LINK = os.getenv("REF_LINK", "stake.us/?c=QKcpH7NE")
RESOURCES_DIR = "resources"
OUTPUT_DIR = "output"

# Fixed the "DIRS =" syntax error
DIRS = [RESOURCES_DIR, OUTPUT_DIR, f"{OUTPUT_DIR}/shorts", f"{OUTPUT_DIR}/seo"]
for d in DIRS: 
    os.makedirs(d, exist_ok=True)

# ==============================================================================
# MODULE 1: VIRAL VIDEO ENGINE (Free API: Pexels + HuggingFace)
# ==============================================================================
class ViralVideoEngine:
    """
    Automates the production of vertical short-form video.
    Integrates Pexels (Video) and Hugging Face (Scripting).
    """
    def __init__(self):
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.hf_key = os.getenv("HUGGINGFACE_API_KEY")
       
    def fetch_footage(self):
        """
        Fetches 'Portrait' orientation video from Pexels.
        """
        queries = ["luxury car", "casino chips", "money counting", "gold bullion", "las vegas night"]
        query = random.choice(queries)
        headers = {'Authorization': self.pexels_key}
        params = {'query': query, 'per_page': 8, 'orientation': 'portrait', 'size': 'medium'}
       
        try:
            r = requests.get('https://api.pexels.com/videos/search', headers=headers, params=params)
            if r.status_code == 200:
                # Fixed the "get('videos',)" syntax error
                videos = r.json().get('videos', [])
                if videos:
                    vid = random.choice(videos)
                    link = vid['video_files'][0]['link']
                    path = f"{RESOURCES_DIR}/temp_video_{int(time.time())}.mp4"
                    logger.info(f"Downloading footage for '{query}'...")
                    with open(path, 'wb') as f:
                        f.write(requests.get(link).content)
                    return path
        except Exception as e:
            logger.error(f"Pexels fetch failed: {e}")
        return None

    def generate_script(self):
        """
        Generates a viral hook using Hugging Face Inference API.
        """
        api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {self.hf_key}"}
        prompt = (
            "Write a single, punchy sentence motivational quote about taking risks and winning wealth. "
            "Do not use cliches. Keep it under 15 words. "
            "End with the phrase 'Link in bio'."
        )
       
        try:
            payload = {"inputs": f" {prompt}"}
            r = requests.post(api_url, headers=headers, json=payload)
            # Simple parsing fallback
            if isinstance(r.json(), list):
                text = r.json()[0]['generated_text']
                # Clean up the output to remove the prompt itself if included
                if prompt in text:
                    text = text.replace(prompt, "").strip()
                return text
            return "Risk everything to win everything. Link in bio."
        except Exception as e:
            logger.error(f"LLM Gen failed: {e}. Using fallback.")
            return "Risk everything to win everything. Link in bio."

    def process_video(self):
        """
        Orchestrates the video creation pipeline.
        """
        logger.info("Starting Video Generation Pipeline...")
        video_path = self.fetch_footage()
        if not video_path: return

        script_text = self.generate_script()
       
        try:
            # Subclip to 8 seconds for high retention
            clip = VideoFileClip(video_path).subclip(0, 8)
           
            # Vertical Crop Logic
            if clip.w > clip.h:
                clip = clip.crop(x_center=clip.w/2, width=1080, height=1920)
           
            # Resize Logic
            clip = clip.resize(height=1920)
            if clip.w != 1080:
                clip = clip.crop(x_center=clip.w/2, width=1080)

            # Text Overlay Logic
            font_path = f"{RESOURCES_DIR}/fonts/Impact.ttf"
            if not os.path.exists(font_path):
                font_path = 'Arial' # Fallback

            txt = TextClip(
                script_text,
                fontsize=70,
                color='yellow',
                font=font_path,
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(900, None)
            )
            txt = txt.set_position(('center', 'center')).set_duration(clip.duration)

            final = CompositeVideoClip([clip, txt])
            output_file = f"{OUTPUT_DIR}/shorts/stake_short_{int(time.time())}.mp4"
           
            # Ensure audio codec is set for compatibility
            final.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac', logger=None)
           
            logger.info(f"SUCCESS: Viral Video generated at {output_file}")
            send_discord_alert(f"🎬 New Viral Short Generated: {output_file}")
           
            os.remove(video_path)
           
        except Exception as e:
            logger.error(f"Video Processing Error: {e}")
            if os.path.exists(video_path): os.remove(video_path)

# ==============================================================================
# MODULE 2: PROGRAMMATIC SEO ENGINE
# ==============================================================================
class PSEOGenerator:
    def __init__(self):
        self.base_keywords = ["stake.us promo code", "stake.us review", "sweepstakes casino"]
   
    def harvest_long_tail(self):
        # Fixed the "expanded =" syntax error
        expanded = []
        modifiers = ["2025", "reddit", "hack", "free sc", "no deposit", "login issue", "app download"]
       
        for b in self.base_keywords:
            for m in modifiers:
                expanded.append(f"{b} {m}")
        
        # Fixed the "deep_tail =" syntax error
        deep_tail = []
        for e in expanded:
            deep_tail.append(f"{e} today")
            deep_tail.append(f"{e} working")

        return expanded + deep_tail

    def build_pages(self):
        logger.info("Starting pSEO Build Process...")
        target_keywords = self.harvest_long_tail()
       
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Best {kw_title} - Official Guide 2025</title>
        </head>
        <body>
            <h1>The Definitive Guide to: {kw_title}</h1>
            <p>Search for <strong>{kw}</strong> ends here.</p>
            <a href="https://{ref_link}">CLAIM 5% RAKEBACK NOW</a>
        </body>
        </html>
        """
       
        count = 0
        for kw in target_keywords:
            fname = kw.replace(' ', '-').replace('.', '').lower() + ".html"
            path = f"{OUTPUT_DIR}/seo/{fname}"
           
            content = html_template.format(
                kw=kw,
                kw_title=kw.title(),
                ref_link=REF_LINK
            )
           
            with open(path, "w") as f:
                f.write(content)
            count += 1
           
        logger.info(f"SUCCESS: Generated {count} SEO landing pages.")
        send_discord_alert(f"🌐 SEO Refresh Complete: {count} pages generated.")

# ==============================================================================
# MAIN LOOP & DB INIT
# ==============================================================================
def init_db():
    db_url = os.getenv("DATABASE_URL", "sqlite:///wenbot.db").replace("sqlite:///", "")
    conn = sqlite3.connect(db_url)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS referrals
                 (user_id TEXT PRIMARY KEY, invites INTEGER DEFAULT 0, balance INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def main():
    logger.info("Booting StakeDominator v2.0...")
    
    # 1. Init DB
    init_db()
    
    # 2. Test Discord
    send_discord_alert("🚀 WenBot is booting up and systems are GO!")

    # 3. Setup Scheduler
    db_path = os.getenv("DATABASE_URL", "sqlite:///wenbot.db")
    jobstores = {
        'default': SQLAlchemyJobStore(url=db_path)
    }
    executors = {
        'default': ThreadPoolExecutor(20),
        'processpool': ThreadPoolExecutor(5)
    }
   
    scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors)
    video_engine = ViralVideoEngine()
    pseo_engine = PSEOGenerator()

    # Schedule Jobs
    scheduler.add_job(video_engine.process_video, 'interval', minutes=1, id='viral_video_gen', replace_existing=True)
    scheduler.add_job(pseo_engine.build_pages, 'interval', minutes=1, id='seo_regen', replace_existing=True)

    try:
        scheduler.start()
        logger.info("Scheduler Started. Press Ctrl+C to exit.")
        # Keep main thread alive
        while True:
            time.sleep(2)
           
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()

if __name__ == "__main__":
    main()
