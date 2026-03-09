import uuid
from datetime import datetime
from sqlalchemy import String, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from src.db.database import Base


class Follow(Base):
    """
    Represents a follow relationship between two users.
    follower_id follows followee_id.
    """
    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint("follower_id", "followee_id", name="uq_follow_pair"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    follower_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    followee_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
