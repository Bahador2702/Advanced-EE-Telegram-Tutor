# init_db_only.py
import asyncio
from db.database import init_db, sync_engine
from db import models

async def main():
    print("Creating tables...")
    models.Base.metadata.create_all(sync_engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    asyncio.run(main())