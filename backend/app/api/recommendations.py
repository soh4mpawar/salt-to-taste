from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.recommendation import SaltySwapRequest, SaltySwapResponse
from app.core.database import get_db
from app.services.swap_service import process_salty_swap
from app.services.rescue_service import get_rescue_strategies
from app.models.recipe import Recipe
from app.models.recipe_salt_recommendation import RecipeSaltRecommendation
from uuid import UUID

router = APIRouter()

@router.get("/{recommendation_id}", status_code=200)
async def get_recommendation(recommendation_id: UUID):
    return {"status": "not_implemented", "endpoint": f"GET /recommendations/{recommendation_id}"}

@router.post("/salty-swap", response_model=SaltySwapResponse, status_code=200)
async def salty_swap(
    request: SaltySwapRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await process_salty_swap(
        recommendation_id=str(request.recommendation_id),
        ingredient_name=request.ingredient_name,
        amount=request.amount,
        unit=request.unit,
        db=db
    )
    return result

@router.post("/rescue")
async def rescue_protocol(
    recommendation_id: str,
    actual_grams_added: float,
    db: AsyncSession = Depends(get_db)
):
    recommendation = await db.get(RecipeSaltRecommendation, recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    recipe = await db.get(Recipe, recommendation.recipe_id)
    context = recommendation.recommendation_context or {}
    dish_type = context.get("dish_type", "other")

    result = get_rescue_strategies(
        dish_type=dish_type,
        actual_grams=actual_grams_added,
        target_grams=float(recommendation.personalized_grams),
        servings=recipe.servings or 4,
        total_mass_grams=float(recipe.total_mass_grams or 800)
    )
    return result
