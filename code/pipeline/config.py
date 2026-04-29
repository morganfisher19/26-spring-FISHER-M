'''
config.py contains all constants and settings

To access config info in other files:
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

'''

# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- API ---
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.congress.gov/v3"

# --- Paths ---
ROOT_DIR = Path(__file__).parents[2]

CODE_DIR = ROOT_DIR / "code" / "pipeline"

DATA_DIR = ROOT_DIR / "data"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"
CACHE_DIR = DATA_DIR / "cache"
REFERENCE_DIR = DATA_DIR / "references"

MEMBER_IMAGE_DIR = ROOT_DIR / "code/frontend/public/images/member_images"

# --- Congress ---
CONGRESS = 119
CURRENT_YEAR = 2026

# --- Database ---
DB_HOST = os.getenv("SERVER")
DB_PORT = 5432
DB_NAME = "congress_db"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("DB_PASSWORD")