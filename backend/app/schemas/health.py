from pydantic import BaseModel, ConfigDict
from typing import Optional

class DailyLogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    recommendation_id: str
    sodium_mg: float
    timestamp: str

class DailySodiumLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    date: str
    total_sodium_mg: float
    entries: list[DailyLogEntry]
    sodium_limit_mg: int
    remaining_mg: float
    percent_used: float
    within_limit: bool

class IngredientSodiumItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    amount: float
    unit: str
    sodium_mg: float
    source: Optional[str] = None
    is_primary_salt: bool

class SodiumBreakdownResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    recipe_id: str
    recipe_title: str
    ingredients: list[IngredientSodiumItem]
    total_hidden_sodium_mg: float
    highest_sodium_ingredient: Optional[str]
    sodium_per_serving_mg: float
    percentage_breakdown: list[dict]

class SodiumLimitUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    sodium_daily_limit_mg: int
    updated: bool
