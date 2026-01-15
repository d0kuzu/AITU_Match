from sqlalchemy import Text, String, BigInteger, Boolean, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from .base import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    target_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("profiles.user_id"), nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    comment: Mapped[str] = mapped_column(String(200), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    target_profile: Mapped["Profile"] = relationship()
