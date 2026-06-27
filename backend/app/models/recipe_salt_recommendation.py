from uuid import UUID, uuid4
from datetime import datetime
from typing import Any
from sqlalchemy import Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.models.base import Base

class RecipeSaltRecommendation(Base):
    __tablename__ = "recipe_salt_recommendations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    recipe_id: Mapped[UUID] = mapped_column(ForeignKey("recipes.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    salt_type_id: Mapped[int] = mapped_column(ForeignKey("salt_types.id"))
    baseline_grams: Mapped[float] = mapped_column(Float, nullable=False)
    personalized_grams: Mapped[float] = mapped_column(Float, nullable=False)
    sodium_mg_per_serving: Mapped[float] = mapped_column(Float, nullable=False)
    recommendation_context: Mapped[dict[str, Any]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
