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
from app.services.palate_service import update_palate_profile_after_feedback, get_palate_summary
from app.core.config import settings

router = APIRouter()

@router.post("", status_code=201, response_model=FeedbackRead)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    db: AsyncSession = Depends(get_db)
):
    # Step 1 — Look up recommendation
    recommendation = await db.get(RecipeSaltRecommendation, feedback_data.recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Step 2 — Look up linked recipe for context
    recipe = await db.get(Recipe, recommendation.recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Step 3 — Extract context from recommendation_context JSONB
    context = recommendation.recommendation_context or {}
    dish_type = context.get("dish_type", "other")
    cooking_method = context.get("cooking_method", "raw")

    # Convert rating if it's an Enum
    rating_val = feedback_data.rating.value if hasattr(feedback_data.rating, 'value') else feedback_data.rating

    # Step 4 — Train VW model
    model_manager = PalateModelManager(model_dir="models")
    success, new_count = await record_feedback(
        user_id=str(recommendation.user_id),
        dish_type=dish_type,
        cooking_method=cooking_method,
        baseline_grams=float(recommendation.baseline_grams),
        servings=recipe.servings or 1,
        rating=rating_val,
        model_manager=model_manager
    )

    # Step 5 — Sync to PostgreSQL
    await update_palate_profile_after_feedback(
        user_id=str(recommendation.user_id),
        rating=rating_val,
        dish_type=dish_type,
        cooking_method=cooking_method,
        feedback_count=new_count,
        db=db
    )

    # Step 6 — Save feedback row
    feedback_row = UserFeedback(
        recommendation_id=feedback_data.recommendation_id,
        rating=feedback_data.rating,
        notes=feedback_data.notes
    )
    db.add(feedback_row)
    await db.commit()
    await db.refresh(feedback_row)

    return feedback_row

@router.get("/palate-summary/{user_id}", status_code=200)
async def get_summary(user_id: str, db: AsyncSession = Depends(get_db)):
    return await get_palate_summary(user_id, db)
