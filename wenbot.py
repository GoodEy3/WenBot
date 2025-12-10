
#!/usr/bin/env python3
"""
StakeAffiliateAutomator v2.0 - The 250X Revenue Engine
Author:
Architecture: Modular, Async, Persistent.
"""

import os
import sys
import time
import logging
import random
import requests
import sqlite3
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Infrastructure Libraries
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

# Media & SEO Libraries
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import praw

load_dotenv()

# --- LOGGING SETUP ---
# Professional logging format for debugging and audit trails
logging.basicConfig(
   level=logging.INFO,
   format='%(asctime)s - [%(module)s] - %(levelname)s - %(message)s',
   handlers=
)
logger = logging.getLogger("StakeDominator")

# --- GLOBAL CONFIGURATION ---
REF_LINK = os.getenv("REF_LINK", "stake.us/?c=QKcpH7NE")
RESOURCES_DIR = "resources"
OUTPUT_DIR = "output"
DIRS =
for d in DIRS: os.makedirs(d, exist_ok=True)

# ==============================================================================
# MODULE 1: VIRAL VIDEO ENGINE (Free API: Pexels + HuggingFace)
# ==============================================================================
class ViralVideoEngine:
   """
   Automates the production of vertical short-form video.
   Integrates Pexels (Video) and Hugging Face (Scripting).
   """
   def __init__(self):
       self.pexels_key = os.getenv("PEXELS_API_KEY")
       self.hf_key = os.getenv("HUGGINGFACE_API_KEY")
       
   def fetch_footage(self):
       """
       Fetches 'Portrait' orientation video from Pexels.
       Uses randomized high-CPM queries to ensure variety.
       """
       queries = ["luxury car", "casino chips", "money counting", "gold bullion", "las vegas night"]
       query = random.choice(queries)
       headers = {'Authorization': self.pexels_key}
       # 'orientation': 'portrait' is crucial for Shorts/Reels optimization
       params = {'query': query, 'per_page': 8, 'orientation': 'portrait', 'size': 'medium'}
       
       try:
           r = requests.get('https://api.pexels.com/videos/search', headers=headers, params=params)
           if r.status_code == 200:
               videos = r.json().get('videos',)
               if videos:
                   # Select random video to avoid repetition
                   vid = random.choice(videos)
                   link = vid['video_files']['link']
                   path = f"{RESOURCES_DIR}/temp_video_{int(time.time())}.mp4"
                   logger.info(f"Downloading footage for '{query}'...")
                   with open(path, 'wb') as f:
                       f.write(requests.get(link).content)
                   return path
       except Exception as e:
           logger.error(f"Pexels fetch failed: {e}")
       return None

   def generate_script(self):
       """
       Generates a viral hook using Hugging Face Inference API.
       Replaces OpenAI to reduce costs to zero.
       """
       # Using Mistral-7B via HF Inference [11]
       api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
       headers = {"Authorization": f"Bearer {self.hf_key}"}
       prompt = (
           "Write a single, punchy sentence motivational quote about taking risks and winning wealth. "
           "Do not use cliches. Keep it under 15 words. "
           "End with the phrase 'Link in bio'."
       )
       
       try:
           payload = {"inputs": f" {prompt}"}
           r = requests.post(api_url, headers=headers, json=payload)
           # Parse HF response
           text = r.json()['generated_text'].split("")[-1].strip().replace('"', '')
           return text
       except Exception as e:
           logger.error(f"LLM Gen failed: {e}. Using fallback.")
           return "Risk everything to win everything. Link in bio."

   def process_video(self):
       """
       Orchestrates the video creation pipeline.
       Uses MoviePy for editing and TextClip for 'Hormozi' style captions.
       """
       logger.info("Starting Video Generation Pipeline...")
       video_path = self.fetch_footage()
       if not video_path: return

       script_text = self.generate_script()
       
       try:
           # Subclip to 8 seconds for high retention
           clip = VideoFileClip(video_path).subclip(0, 8)
           
           # Vertical Crop Logic: Ensure 9:16 Aspect Ratio [24]
           if clip.w > clip.h:
               clip = clip.crop(x_center=clip.w/2, width=1080, height=1920)
           
           # Resize Logic: Standardize to 1080p width
           clip = clip.resize(height=1920)
           if clip.w!= 1080:
                clip = clip.crop(x_center=clip.w/2, width=1080)

           # Text Overlay Logic
           # Note: We use a specific TTF file to ensure compatibility across systems
           # 'Impact' font is standard for memes/shorts.
           font_path = f"{RESOURCES_DIR}/fonts/Impact.ttf"
           if not os.path.exists(font_path):
               # Fallback if font missing
               font_path = 'Arial-Bold'

           txt = TextClip(
               script_text,
               fontsize=80,
               color='yellow',
               font=font_path,
               stroke_color='black',
               stroke_width=4,
               method='caption',
               size=(900, None) # Constrain width for margins
           )
           # Position text in center
           txt = txt.set_position(('center', 'center')).set_duration(clip.duration)

           # Composite
           final = CompositeVideoClip([clip, txt])
           output_file = f"{OUTPUT_DIR}/shorts/stake_short_{int(time.time())}.mp4"
           
           # Render (Audio codec aac is required for YouTube/TikTok)
           final.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac', logger=None)
           
           logger.info(f"SUCCESS: Viral Video generated at {output_file}")
           
           # Cleanup temp file
           os.remove(video_path)
           
       except Exception as e:
           logger.error(f"Video Processing Error: {e}")
           if os.path.exists(video_path): os.remove(video_path)

# ==============================================================================
# MODULE 2: PROGRAMMATIC SEO ENGINE (Jinja2 + AutoSuggest)
# ==============================================================================
class PSEOGenerator:
   """
   Generates thousands of static HTML landing pages based on
   long-tail keywords harvested from Google Autosuggest.
   """
   def __init__(self):
       self.base_keywords = ["stake.us promo code", "stake.us review", "sweepstakes casino"]
   
   def harvest_long_tail(self):
       """
       Simulates Google Autosuggest Harvesting.
       In production, this hits 'http://google.com/complete/search' with proxy rotation.
       """
       # Expanding the seed list to simulate 'harvesting' 100+ keywords [29]
       expanded =
       modifiers = ["2025", "reddit", "hack", "free sc", "no deposit", "login issue", "app download"]
       
       for b in self.base_keywords:
           for m in modifiers:
               expanded.append(f"{b} {m}")
       
       # Add a recursive layer (simulated)
       deep_tail =
       for e in expanded:
           deep_tail.append(f"{e} today")
           deep_tail.append(f"{e} working")
           
       return expanded + deep_tail

   def build_pages(self):
       """
       Generates static HTML files using Jinja2 logic.
       Injects the Affiliate Link and Schema Markup.
       """
       logger.info("Starting pSEO Build Process...")
       target_keywords = self.harvest_long_tail()
       
       # Highly optimized HTML template for conversion
       # Includes Schema.org markup for Rich Snippets
       html_template = """
       <!DOCTYPE html>
       <html lang="en">
       <head>
           <meta charset="UTF-8">
           <meta name="viewport" content="width=device-width, initial-scale=1.0">
           <title>Best {kw_title} - Official Guide 2025</title>
           <meta name="description" content="Looking for {kw}? Use the official Stake.us code for 5% Rakeback. Verified today.">
           <script type="application/ld+json">
           {{
             "@context": "https://schema.org/",
             "@type": "Product",
             "name": "Stake.us Promo Code",
             "aggregateRating": {{
               "@type": "AggregateRating",
               "ratingValue": "4.9",
               "ratingCount": "1250"
             }}
           }}
           </script>
           <style>
               body {{ font-family: sans-serif; background: #1a1a1a; color: #fff; max-width: 800px; margin: 0 auto; padding: 20px; }}
              .cta-button {{ background: #00e701; color: #000; padding: 20px; text-decoration: none; font-weight: bold; font-size: 24px; display: block; text-align: center; border-radius: 5px; margin: 30px 0; }}
               table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
               td, th {{ border: 1px solid #444; padding: 10px; text-align: left; }}
           </style>
       </head>
       <body>
           <h1>The Definitive Guide to: {kw_title}</h1>
           <p>Players searching for <strong>{kw}</strong> often miss out on the best rakeback deals.</p>
           <p>Our exclusive partnership ensures you get the maximum starting balance.</p>
           
           <a href="https://{ref_link}" class="cta-button">CLAIM 5% RAKEBACK NOW</a>
           
           <h2>Stake.us vs Competitors</h2>
           <table>
               <tr><th>Feature</th><th>Stake.us</th><th>Others</th></tr>
               <tr><td>Rakeback</td><td>5% (Exclusive)</td><td>None</td></tr>
               <tr><td>Instant Cashout</td><td>Yes (Crypto)</td><td>No (3-5 Days)</td></tr>
           </table>

           <footer>
               <p>Updated: {date} | <a href="index.html">Home</a></p>
           </footer>
       </body>
       </html>
       """
       
       count = 0
       for kw in target_keywords:
           # File name sanitization
           fname = kw.replace(' ', '-').replace('.', '').lower() + ".html"
           path = f"{OUTPUT_DIR}/seo/{fname}"
           
           content = html_template.format(
               kw=kw,
               kw_title=kw.title(),
               ref_link=REF_LINK,
               date=datetime.now().strftime("%Y-%m-%d")
           )
           
           with open(path, "w") as f:
               f.write(content)
           count += 1
           
       logger.info(f"SUCCESS: Generated {count} SEO landing pages ready for deployment.")

# ==============================================================================
# MODULE 3: INFRASTRUCTURE & SCHEDULING (APScheduler + SQLite)
# ==============================================================================
def init_db():
   """
   Initialize SQLite DB for the Community Bot module.
   Persistent storage for referral tracking and user points.
   """
   conn = sqlite3.connect(os.getenv("DATABASE_URL").replace("sqlite:///", ""))
   c = conn.cursor()
   # Referral Tracking Table
   c.execute('''CREATE TABLE IF NOT EXISTS referrals
                (user_id TEXT PRIMARY KEY, invites INTEGER DEFAULT 0, balance INTEGER DEFAULT 0)''')
   conn.commit()
   conn.close()

def main():
   logger.info("Booting StakeDominator v2.0 (250X Engine)...")
   init_db()

   # APScheduler Setup with SQLite Persistence [14]
   # This allows jobs to survive restarts.
   jobstores = {
       'default': SQLAlchemyJobStore(url=os.getenv("DATABASE_URL"))
   }
   executors = {
       'default': ThreadPoolExecutor(20), # For I/O bound tasks (Scraping)
       'processpool': ThreadPoolExecutor(5) # For CPU bound tasks (Video Rendering)
   }
   
   # BackgroundScheduler allows the script to run without blocking the terminal
   scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors)

   # Instantiate Engines
   video_engine = ViralVideoEngine()
   pseo_engine = PSEOGenerator()

   # --- JOB SCHEDULES ---
   
   # 1. Viral Video Loop: Every 4 hours (6 videos/day)
   # This floods the algorithmic feed with fresh content.
   scheduler.add_job(
       video_engine.process_video,
       'interval',
       hours=4,
       id='viral_video_gen',
       replace_existing=True
   )
   
   # 2. SEO Refresh: Every 24 hours
   # Updates dates and content to keep pages "Fresh" for Google.
   scheduler.add_job(
       pseo_engine.build_pages,
       'interval',
       hours=24,
       id='seo_regen',
       replace_existing=True
   )

   # 3. (Placeholder) Reddit Monitor
   # Typically runs every 15 mins to check for new keyword mentions.
   # scheduler.add_job(reddit_monitor.scan, 'interval', minutes=15)

   try:
       scheduler.start()
       logger.info("Scheduler Started. System is autonomous. Press Ctrl+C to exit.")
       
       # Keep main thread alive to allow scheduler background threads to run
       while True:
           time.sleep(2)
           
   except (KeyboardInterrupt, SystemExit):
       logger.info("Shutting down scheduler...")
       scheduler.shutdown()

if __name__ == "__main__":
   main()
