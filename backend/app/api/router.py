from fastapi import APIRouter

from app.api.users import router as users_router
from app.api.recipes import router as recipes_router
from app.api.recommendations import router as recommendations_router
from app.api.feedback import router as feedback_router
from app.api.salt import router as salt_router

api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(recipes_router, prefix="/recipes", tags=["recipes"])
api_router.include_router(recommendations_router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(feedback_router, prefix="/feedback", tags=["feedback"])
api_router.include_router(salt_router, tags=["salt"])
