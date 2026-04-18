import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.llm7.io/v1")
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
    
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/tutor_bot.db")
    VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", "./data/vector_store")
    UPLOADS_DIR = os.getenv("UPLOADS_DIR", "./data/uploads")
    
    # Ensure directories exist
    os.makedirs("./data", exist_ok=True)
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    COURSES = {
        "signals": "سیگنال‌ها و سیستم‌ها",
        "circuits": "مدارهای الکتریکی ۱ و ۲",
        "em": "الکترومغناطیس",
        "electronics": "الکترونیک ۱ و ۲",
        "digital": "سیستم‌های دیجیتال",
        "machines": "ماشین‌های الکتریکی"
    }
