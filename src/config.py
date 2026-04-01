from os import getcwd, getenv, makedirs
from pathlib import Path

from dotenv import load_dotenv


PARENT_DIR = Path(getcwd()).parent
STORAGE_DIR = PARENT_DIR / "storage"
STATIC_DIR = PARENT_DIR / "static"
TEMPLATES_DIR = PARENT_DIR / "templates"

makedirs(STORAGE_DIR, exist_ok=True)

load_dotenv(PARENT_DIR / ".env")

DATABASE_URL = f"postgresql+asyncpg://{getenv('DB_USER')}:{getenv('DB_PASS')}@{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"
DATABASE_URL_UTILS = DATABASE_URL.replace("asyncpg", "psycopg")
