from sqlalchemy.ext.asyncio import async_sessionmaker

from database.session import get_db


class Repo:
    def __init__(self, session):
        self.session = session
