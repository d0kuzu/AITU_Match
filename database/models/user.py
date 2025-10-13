from sqlalchemy import Text, String, BigInteger, Boolean, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    profile: Mapped["Profile"] = relationship(back_populates="user", cascade="all, delete-orphan")
    barcode: Mapped["Barcode"] = relationship(back_populates="user", cascade="all, delete-orphan")