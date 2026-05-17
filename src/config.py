import tempfile
from os import getcwd, getenv, makedirs
from pathlib import Path

from dotenv import load_dotenv


PARENT_DIR = Path(getcwd()).parent
STORAGE_DIR = PARENT_DIR / "storage"
TEMPDIR = PARENT_DIR / "tmp"
STATIC_DIR = PARENT_DIR / "static"
TEMPLATES_DIR = PARENT_DIR / "templates"

makedirs(STORAGE_DIR, exist_ok=True)
makedirs(TEMPDIR, exist_ok=True)

tempfile.tempdir = TEMPDIR

is_loaded = load_dotenv(PARENT_DIR / ".env")
if not is_loaded:
    raise FileNotFoundError("The .env file does not exist")

DATABASE_URL = f"postgresql+asyncpg://{getenv('DB_USER')}:{getenv('DB_PASS')}@{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"
DATABASE_URL_UTILS = DATABASE_URL.replace("asyncpg", "psycopg")
