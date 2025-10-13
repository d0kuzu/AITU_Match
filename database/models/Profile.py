from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, Integer, Text, DateTime, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from .base import Base


class Profile(Base):
    __tablename__ = "profiles"

    user: Mapped["User"] = mapped_column(ForeignKey("users.profile"), primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    sex: Mapped[SexEnum] = mapped_column(Enum(SexEnum), nullable=False)
    uni: Mapped[UniEnum] = mapped_column(Enum(UniEnum), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    s3_path: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship(back_populates="profile", cascade="all, delete-orphan")