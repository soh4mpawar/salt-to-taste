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
    low_sodium_warning: str | None = None
    herb_suggestions: list[str] | None = None

class SaltySwapRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    recommendation_id: UUID
    ingredient_name: str      # e.g. "soy sauce"
    amount: float             # quantity added
    unit: str                 # "tbsp", "tsp", "ml", "g"

class SaltySwapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ingredient_name: str
    added_sodium_mg: float
    equivalent_salt_grams: float
    original_recommendation_grams: float
    adjusted_grams: float
    adjustment_applied: bool
    recommendation: str
    warning: str | None = None
