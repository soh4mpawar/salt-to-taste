from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class PalateHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rating: str
    notes: Optional[str] = None
    created_at: datetime
    baseline_grams: float
    personalized_grams: float
    recommendation_context: Optional[dict] = None
