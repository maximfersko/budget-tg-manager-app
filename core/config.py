import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN not found in .env!")

DB_URL = os.getenv("DB_URL", "postgresql+asyncpg://postgres:postgres@db:5432/budget_db")
