from fastapi import APIRouter
from app.schemas.user import UserCreate, UserUpdate
from uuid import UUID

router = APIRouter()

@router.post("", status_code=201)
async def create_user(user: UserCreate):
    return {"status": "not_implemented", "endpoint": "POST /users"}

@router.get("/{user_id}", status_code=200)
async def get_user(user_id: UUID):
    return {"status": "not_implemented", "endpoint": f"GET /users/{user_id}"}

@router.patch("/{user_id}", status_code=200)
async def update_user(user_id: UUID, user: UserUpdate):
    return {"status": "not_implemented", "endpoint": f"PATCH /users/{user_id}"}
