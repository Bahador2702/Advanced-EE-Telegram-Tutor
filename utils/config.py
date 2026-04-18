import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from parent directory
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Central configuration manager"""
    
    # ========== Telegram ==========
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # ========== LLM Configuration (OpenAI-compatible) ==========
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    
    # ========== Embedding Configuration ==========
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", LLM_API_KEY)
    EMBEDDING_BASE_URL: str = os.getenv("EMBEDDING_BASE_URL", LLM_BASE_URL)
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # ========== Paths ==========
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    COURSES_DIR: str = os.path.join(DATA_DIR, "courses")
    DB_PATH: str = os.path.join(DATA_DIR, "tutor.db")
    LOGS_DIR: str = os.getenv("LOGS_DIR", "./logs")
    
    # ========== Chunking ==========
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # ========== Retrieval ==========
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    HYBRID_SEARCH_ALPHA: float = float(os.getenv("HYBRID_SEARCH_ALPHA", "0.5"))
    
    # ========== Memory ==========
    MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
    
    # ========== Rate Limiting ==========
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    
    # ========== Logging ==========
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # ========== Voice ==========
    VOICE_ENABLED: bool = os.getenv("VOICE_ENABLED", "False").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        errors = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY is required")
        if not cls.LLM_BASE_URL:
            errors.append("LLM_BASE_URL is required")
            
        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(errors))
        
        # Create directories if not exist
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.COURSES_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
        
        return True
    
    @classmethod
    def display(cls) -> str:
        """Show config (hide sensitive data)"""
        return f"""
        Telegram Bot: {'✅' if cls.TELEGRAM_BOT_TOKEN else '❌'}
        LLM Base URL: {cls.LLM_BASE_URL}
        LLM Model: {cls.LLM_MODEL}
        Embedding Model: {cls.EMBEDDING_MODEL}
        Data Dir: {cls.DATA_DIR}
        Chunk Size: {cls.CHUNK_SIZE}
        Top K: {cls.TOP_K_RETRIEVAL}
        """


config = Config()