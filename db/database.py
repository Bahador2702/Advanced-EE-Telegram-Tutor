import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from utils.config import config

# Create data directory if not exists
data_dir = Path(config.DATA_DIR)
data_dir.mkdir(parents=True, exist_ok=True)

# SQLite database path
db_path = data_dir / "tutor.db"

# Async database URL for SQLite
ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

# Sync database URL (for migrations)
SYNC_DATABASE_URL = f"sqlite:///{db_path}"

# Create async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
)

# Create sync engine (for non-async operations)
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def init_db():
    """Initialize database - create all tables"""
    from db import models  # Import here to avoid circular imports
    
    # Create tables using sync engine first (more reliable)
    print("Creating database tables...")
    Base.metadata.create_all(sync_engine)
    
    # Also try with async engine
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database initialized successfully")


async def get_db_session() -> AsyncSession:
    """Get database session (dependency injection)"""
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_session():
    """Get sync database session for non-async operations"""
    from sqlalchemy.orm import sessionmaker
    SyncSessionLocal = sessionmaker(bind=sync_engine)
    return SyncSessionLocal()