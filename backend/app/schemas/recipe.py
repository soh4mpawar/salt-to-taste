from uuid import UUID
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict
from app.models.recipe import SourceTypeEnum
from app.schemas.recommendation import RecommendationRead

class RecipeCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    source_url: str | None = None
    source_type: SourceTypeEnum
    raw_content: str

class RecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    title: str
    source_url: str | None = None
    source_type: SourceTypeEnum
    raw_content: str
    parsed_json: dict[str, Any] | None = None
    total_mass_grams: float | None = None
    servings: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    recommendations: list[RecommendationRead] = []

class RecipeList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    created_at: datetime

class RecipeImageUploadResponse(RecommendationRead):
    extraction_method: str | None = None
    ocr_confidence: str | float | None = None
