from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=10, pool_pre_ping=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
