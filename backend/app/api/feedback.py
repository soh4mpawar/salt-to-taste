import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackRead
from app.models.user_feedback import UserFeedback
from app.models.recipe_salt_recommendation import RecipeSaltRecommendation
from app.models.recipe import Recipe
from app.agents.personalization_engine import record_feedback, PalateModelManager
from app.core.config import settings

router = APIRouter()

@router.post("", response_model=FeedbackRead, status_code=201)
async def create_feedback(feedback_in: FeedbackCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(RecipeSaltRecommendation).where(RecipeSaltRecommendation.id == feedback_in.recommendation_id)
    result = await db.execute(stmt)
    recommendation = result.scalars().first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    feedback = UserFeedback(
        recommendation_id=feedback_in.recommendation_id,
        rating=feedback_in.rating,
        notes=feedback_in.notes
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    
    context = recommendation.recommendation_context or {}
    dish_type = context.get("dish_type", "other")
    cooking_method = context.get("cooking_method", "simmer")
    baseline_grams = recommendation.baseline_grams
    
    rec_stmt = select(Recipe).where(Recipe.id == recommendation.recipe_id)
    rec_result = await db.execute(rec_stmt)
    recipe = rec_result.scalars().first()
    servings = recipe.servings if recipe and recipe.servings else 1
    
    model_dir = os.path.dirname(settings.VW_MODEL_PATH) or "models"
    model_manager = PalateModelManager(model_dir=model_dir)
    
    await record_feedback(
        user_id=str(recommendation.user_id),
        dish_type=dish_type,
        cooking_method=cooking_method,
        baseline_grams=baseline_grams,
        servings=servings,
        rating=feedback_in.rating.value,
        model_manager=model_manager
    )
    
    return FeedbackRead.model_validate(feedback)
