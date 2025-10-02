import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))  # Group chat ID for admins

# Database
DB_PATH = 'bot_database.db'

# File paths
PRIVACY_POLICY_PATH = 'privacy_policy.pdf'
PHOTOS_DIR = 'photos'
STUDENT_IDS_DIR = 'student_ids'

# Matching settings
MAX_PROFILES_PER_SEARCH = 100

# Create directories if they don't exist
os.makedirs(PHOTOS_DIR, exist_ok=True)
os.makedirs(STUDENT_IDS_DIR, exist_ok=True)