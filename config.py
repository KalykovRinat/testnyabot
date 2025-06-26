from itertools import chain
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
Review = int(os.getenv("REVIEW_CHAT_ID"))
chat_admin = int(os.getenv("ADMIN_CHAT_ID"))

ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
LANGUAGES = os.getenv("LANGUAGES", "ru").split(",")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "db": os.getenv("DB_NAME"),
}
