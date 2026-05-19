import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

YANDEX_CLOUD_FOLDER = os.getenv("YANDEX_CLOUD_FOLDER", "")
YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY", "")
YANDEX_CLOUD_MODEL = os.getenv("YANDEX_CLOUD_MODEL", "qwen3.6-35b-a3b/latest")

PARQUET_DIR = BASE_DIR / "dumps" / "fedstatru" / "fedstatru" / "data" / "parquet"
CSV_PATH = BASE_DIR / "knowledge_base_fedstatru_real.csv"
DB_PATH = BASE_DIR / "my_db.duckdb"
