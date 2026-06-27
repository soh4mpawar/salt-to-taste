from uuid import UUID
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict

class RecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    recipe_id: UUID
    user_id: UUID
    salt_type_id: int
    salt_type_name: str
    baseline_grams: float
    personalized_grams: float
    sodium_mg_per_serving: float
    recommendation_context: dict[str, Any] | None = None
    created_at: datetime

class SaltySwapRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    recipe_id: UUID
    ingredient_name: str
    sodium_mg: float

class SaltySwapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    adjusted_grams: float
    explanation: str
