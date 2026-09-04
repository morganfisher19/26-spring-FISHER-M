import os
from pathlib import Path
from dotenv import load_dotenv

'''
DEV VS. PROD:
- Default set to dev
- If you want to run in prod launch with: APP_ENV=prod python app.py
- Can change in run.bat file
'''
ACTIVE_ENV = os.getenv("ENVIRONMENT", "dev") # CHANGE THIS FROM DEV TO PROD

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / f".env.{ACTIVE_ENV}")
print(f"Loaded env file: {ROOT_DIR / f'.env.{ACTIVE_ENV}'} | exists: {(ROOT_DIR / f'.env.{ACTIVE_ENV}').exists()}")

def required(name: str) -> str:
    # Raises an error if a required variable is missing
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )
    return value

def build_db_url() -> str:
    return (
        f"postgresql://{required('DB_USER')}:{required('DB_PASSWORD')}"
        f"@{required('DB_HOST')}:{os.getenv('DB_PORT', '5432')}/{required('DB_NAME')}"
    )

class BaseConfig:
    # SECRET_KEY = required("SECRET_KEY")
    DB_URL = build_db_url()
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DEBUG = False

class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    DEBUG = False

CONFIG_MAP = {"dev": DevConfig, "prod": ProdConfig}