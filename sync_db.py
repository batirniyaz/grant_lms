
import asyncio
from auth.model import Base
from db.db import engine
from backend.models.group_model import Group # Ensure all models are loaded

async def sync_db():
    print("Connecting to database to sync tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database sync complete!")

if __name__ == "__main__":
    asyncio.run(sync_db())
