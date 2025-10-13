from sqlalchemy import Text, String, BigInteger, Boolean, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from .base import Base

class Barcode(Base):
    __tablename__ = "barcodes"

    code: Mapped[int] = mapped_column(String, ForeignKey("users.user_id"), primary_key=True)