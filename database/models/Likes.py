from sqlalchemy import Integer, ForeignKey, BigInteger, Boolean, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.models import Base


class Like(Base):
    __tablename__ = "likes"

    like_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    liker_user_id: Mapped[str] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    liked_user_id: Mapped[str] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)

    is_accepted: Mapped[bool] = mapped_column(Boolean, nullable=True, default=text("TRUE"))
