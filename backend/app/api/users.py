from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserRead
from uuid import UUID
from datetime import datetime

router = APIRouter()

@router.post("", status_code=201)
async def create_user(user: UserCreate):
    return {"status": "not_implemented", "endpoint": "POST /users"}

@router.get("/{user_id}", status_code=200)
async def get_user(user_id: UUID):
    return {"status": "not_implemented", "endpoint": f"GET /users/{user_id}"}

@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user
