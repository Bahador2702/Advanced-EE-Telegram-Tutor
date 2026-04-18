import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # LLM (OpenAI-compatible)
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.llm7.io/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
    
    # Embedding (optional, use same if not specified)
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", LLM_API_KEY)
    EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", LLM_BASE_URL)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Paths
    DATA_DIR = os.getenv("DATA_DIR", "./data")
    COURSES_DIR = os.path.join(DATA_DIR, "courses")
    DB_PATH = f"sqlite+aiosqlite:///{os.path.join(DATA_DIR, 'tutor.db')}"
    
    # Chunking
    MAX_CHUNK_SIZE = int(os.getenv("MAX_CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Memory
    MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # seconds
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not cls.LLM_API_KEY:
            raise ValueError("LLM_API_KEY is required")
        
        # Ensure directories exist
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.COURSES_DIR, exist_ok=True)
        return True

config = Config()
