from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.user_feedback import RatingEnum

class FeedbackCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    recommendation_id: UUID
    rating: RatingEnum
    notes: str | None = None

class FeedbackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    recommendation_id: UUID
    rating: RatingEnum
    notes: str | None = None
    created_at: datetime
