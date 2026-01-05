from datetime import datetime
from sqlalchemy import String, Text, DateTime, Float, Column
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Image
    image_filename: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_status: Mapped[str] = mapped_column(
        String, nullable=False, default="READY"
    )

    # Image description (AI)
    image_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_status: Mapped[str] = mapped_column(
        String, nullable=False, default="NONE"
    )

    # Post content
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    username: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    # Sentiment analysis
    sentiment_status: Mapped[str] = mapped_column(
        String, nullable=False, default="NONE"
    )
    sentiment_label: Mapped[str | None] = mapped_column(String, nullable=True)
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)