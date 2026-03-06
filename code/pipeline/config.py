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

# --- Congress ---
CONGRESS = 119
CURRENT_YEAR = 2026

# --- Database ---
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_PORT = os.getenv("DB_PORT", 5432)
# DB_NAME = os.getenv("DB_NAME")
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")


# Known record counts (update these when re-running to get latest data)
MEMBER_COUNT = 538
BILL_COUNT = 13250
AMENDMENT_COUNT = 4455
HOUSE_VOTE_COUNTS = {1: 362, 2: 78}  # session: count