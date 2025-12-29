from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, Integer, Text, DateTime, Enum, func, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship

from config.enums import SexEnum, UniEnum, OppositeSexEnum
from .base import Base


class Profile(Base):
    __tablename__ = "profiles"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    sex: Mapped[SexEnum] = mapped_column(Enum(SexEnum), nullable=False)
    opposite_sex: Mapped[OppositeSexEnum] = mapped_column(Enum(OppositeSexEnum), nullable=False)
    uni: Mapped[UniEnum] = mapped_column(Enum(UniEnum), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    s3_path: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())