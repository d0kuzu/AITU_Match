import logging

from database.session import engine
from database.models import *


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("database connected")

async def close_db():
    await engine.dispose()
    print("database connection closed")