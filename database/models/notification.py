from sqlalchemy import Integer, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.enums import ActionEnum
from database.models import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    action_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("actions.id"), nullable=True)

    action: Mapped["Action"] = relationship()
