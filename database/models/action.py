from datetime import datetime

from sqlalchemy import Integer, ForeignKey, BigInteger, DateTime, text, UniqueConstraint, Enum, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from config.enums import ActionEnum, ActionStatusEnum
from database.models import Base


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    action_type: Mapped[ActionEnum] = mapped_column(Enum(ActionEnum), nullable=False)

    target_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    status: Mapped[ActionStatusEnum] = mapped_column(Enum(ActionStatusEnum), nullable=False)

    message: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_target_user_id", "target_id"),
        Index("idx_user_target", "user_id", "target_id", unique=True),
    )
