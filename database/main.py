import logging

from database.session import get_engine, init
from database.models import *


async def init_db(asyncpg_url: str):
    init(asyncpg_url)
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        # await conn.run_sync(Base.metadata.create_all)
    print("database connected")

async def close_db():
    await get_engine().dispose()
    print("database connection closed")