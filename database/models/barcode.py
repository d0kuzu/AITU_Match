from sqlalchemy import Text, String, BigInteger, Boolean, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from .base import Base

class Barcode(Base):
    __tablename__ = "barcodes"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))

    user: Mapped["User"] = relationship(back_populates="user", cascade="all, delete-orphan")
