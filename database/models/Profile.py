from sqlalchemy import BigInteger, ForeignKey, String, Integer, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from .base import Base

class Profile(Base):
    __tablename__ = "profiles"

    user: Mapped["User"] = mapped_column(ForeignKey("users.profile"), primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    sex: Mapped[SexEnum] = mapped_column(String, nullable=False)
    uni: Mapped[UniEnum] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=True, server_default=text("true")
    )

    s3_path: Mapped[Str1024] = mapped_column(nullable=False)

    created_at: Mapped[created_at_type]
    modified_at: Mapped[modified_at_type]

    user: Mapped["User"] = relationship(
        back_populates="profile",
    )