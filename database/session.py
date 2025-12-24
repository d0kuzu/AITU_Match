from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker

engine: AsyncEngine
AsyncSessionLocal :async_sessionmaker[AsyncSession]

def init(asyncpg_url: str):
    global engine, AsyncSessionLocal
    engine = create_async_engine(asyncpg_url, echo=True)

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

def get_engine():
    global engine
    return engine

@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
