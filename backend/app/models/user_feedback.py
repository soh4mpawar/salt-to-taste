from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class RatingEnum(str, enum.Enum):
    perfect = "perfect"
    too_salty = "too_salty"
    needs_more = "needs_more"

class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    recommendation_id: Mapped[UUID] = mapped_column(ForeignKey("recipe_salt_recommendations.id"))
    rating: Mapped[RatingEnum] = mapped_column(SQLEnum(RatingEnum, name="rating_enum"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
