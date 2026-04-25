import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")