from uuid import UUID, uuid4
from datetime import datetime
from typing import Any
from sqlalchemy import String, Text, DateTime, ForeignKey, Float, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class SourceTypeEnum(str, enum.Enum):
    url = "url"
    text = "text"
    image = "image"

class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String)
    source_type: Mapped[SourceTypeEnum] = mapped_column(SQLEnum(SourceTypeEnum, name="source_type_enum"), nullable=False)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_json: Mapped[dict[str, Any]] = mapped_column(JSONB)
    total_mass_grams: Mapped[float | None] = mapped_column(Float)
    servings: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())
