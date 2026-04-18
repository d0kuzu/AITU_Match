from sqlalchemy import BigInteger
from sqlalchemy.orm import mapped_column, Mapped
from .base import Base

class Ban(Base):
    __tablename__ = "bans"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
