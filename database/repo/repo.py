from sqlalchemy.ext.asyncio import AsyncSession


class Repo:
    def __init__(self, session):
        self.session: AsyncSession = session
