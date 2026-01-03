from datetime import datetime
from sqlalchemy import String, Text, DateTime, Float, Column
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    image_filename: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_status: Mapped[str] = mapped_column(String, nullable=False, default="READY")
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    username: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    sentiment_status = Column(String, nullable=False, default="NONE")
    sentiment_label = Column(String, nullable=True)
    sentiment_score = Column(Float, nullable=True)
