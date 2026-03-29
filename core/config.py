import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN not found in .env!")

DB_URL = os.getenv("DB_URL")
REDIS_URL = os.getenv("REDIS_URL")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")