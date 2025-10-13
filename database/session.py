from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from config import env

engine: AsyncEngine = create_async_engine(env.asyncpg_url, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
