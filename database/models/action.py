from sqlalchemy import Integer, ForeignKey, BigInteger, Boolean, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.models import Base


class Action(Base):
    __tablename__ = "actions"

    like_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    action_owner: Mapped[str] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    action_target: Mapped[str] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)

    action_type: Mapped[str] = mapped_column(Text, nullable=False)
