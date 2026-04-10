import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN not found in .env!")

_first_admin_raw = (os.getenv("FIRST_ADMIN_ID") or "751575780").strip()
FIRST_ADMIN_ID = int(_first_admin_raw)

_db_url_raw = os.getenv("DB_URL")
DB_URL = (_db_url_raw or "").strip() or None


def _redis_host() -> str:
    h = (os.getenv("REDIS_HOST") or "").strip()
    if not h or h.startswith("${"):
        return "127.0.0.1"
    return h


def _redis_port() -> int:
    raw = (os.getenv("REDIS_PORT") or "6379").strip()
    if not raw or raw.startswith("${"):
        return 6379
    try:
        return int(raw)
    except ValueError:
        return 6379


def _redis_url_resolved() -> str:
    raw = (os.getenv("REDIS_URL") or "").strip()
    if raw and "${" not in raw:
        return raw
    return f"redis://{_redis_host()}:{_redis_port()}"


REDIS_URL = _redis_url_resolved()

_rabbit_raw = os.getenv("RABBITMQ_URL")
RABBITMQ_URL = (_rabbit_raw or "").strip() or None

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "budget-files")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

INTERNAL_TRANSFER_KEYWORDS = [
    kw.strip().lower() 
    for kw in os.getenv("INTERNAL_TRANSFER_KEYWORDS", "").split(",") 
    if kw.strip()
]

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
_qdrant_port_raw = (os.getenv("QDRANT_PORT") or "6333").strip()
QDRANT_PORT = int(_qdrant_port_raw)
