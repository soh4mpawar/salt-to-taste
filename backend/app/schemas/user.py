from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr
    display_name: str | None = None
    sodium_daily_limit_mg: int | None = None
    low_sodium_mode: bool = False

class UserCreate(UserBase):
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr | None = None
    display_name: str | None = None
    sodium_daily_limit_mg: int | None = None
    low_sodium_mode: bool | None = None

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
