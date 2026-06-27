from uuid import UUID, uuid4
from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.models.base import Base

class PalateProfile(Base):
    __tablename__ = "palate_profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    weights_json: Mapped[dict[str, Any]] = mapped_column(JSONB)
    dish_context_weights: Mapped[dict[str, Any]] = mapped_column(JSONB)
    total_feedback_count: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
