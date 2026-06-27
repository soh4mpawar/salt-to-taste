from uuid import UUID
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from app.models.recipe import SourceTypeEnum
from app.schemas.recommendation import RecommendationRead

class RecipeCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    source_url: str | None = None
    source_type: SourceTypeEnum
    raw_content: str
    low_sodium_mode: bool = False
    user_id: Optional[str] = None

class RecipeSourceInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    source_type: str
    extraction_method: Optional[str]
    ocr_confidence: Optional[str]
    parsing_warnings: Optional[list[str]]

class RecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    title: str
    source_url: str | None = None
    source_type: SourceTypeEnum
    raw_content: str
    parsed_json: dict[str, Any] | None = None
    source_info: Optional[RecipeSourceInfo] = None
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
