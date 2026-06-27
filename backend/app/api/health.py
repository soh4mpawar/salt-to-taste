from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.recipe_salt_recommendation import RecipeSaltRecommendation
from app.models.recipe import Recipe
from app.models.user import User
from app.services.user_service import get_user_sodium_limit, update_user_sodium_limit
from app.services.sodium_tracking_service import get_daily_sodium, get_weekly_sodium_summary
from app.services.sodium_breakdown_service import calculate_ingredient_breakdown
from app.schemas.health import DailySodiumLog, SodiumLimitUpdate

router = APIRouter()

def _get_health_recommendations(avg_sodium: float, limit: int) -> list[str]:
    recs = []
    if avg_sodium > limit * 0.5:
        recs.append("Your recent recipes average over 50% of your daily sodium limit per serving. Consider enabling Low-Sodium Mode.")
    if avg_sodium < limit * 0.15:
        recs.append("Your sodium intake appears very low. Ensure you are adequately seasoning food for food safety and palatability.")
    if not recs:
        recs.append("Your sodium intake from recent recipes looks healthy.")
    return recs

@router.get("/sodium-report/{user_id}")
async def get_sodium_report(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Get user's sodium limit
    limit = await get_user_sodium_limit(user_id, db)

    # Get weekly summary
    weekly = await get_weekly_sodium_summary(user_id, db)

    # Get today's log
    today = await get_daily_sodium(user_id, db=db)

    # Get user's last 5 recommendations for trend
    result = await db.execute(
        select(RecipeSaltRecommendation)
        .where(RecipeSaltRecommendation.user_id == user_id)
        .order_by(RecipeSaltRecommendation.created_at.desc())
        .limit(5)
    )
    recent_recs = result.scalars().all()

    avg_sodium = (
        sum(float(r.sodium_mg_per_serving) for r in recent_recs) / len(recent_recs)
        if recent_recs else 0.0
    )

    user = await db.get(User, user_id)
    limit_source = "user_custom" if (user and user.sodium_daily_limit_mg) else "aha_default"

    return {
        "user_id": user_id,
        "sodium_limit_mg": limit,
        "limit_source": limit_source,
        "today": today,
        "weekly_summary": weekly,
        "recent_recipes": {
            "count": len(recent_recs),
            "average_sodium_per_serving_mg": round(avg_sodium, 1),
            "trending": "high" if avg_sodium > limit * 0.4 else "normal"
        },
        "recommendations": _get_health_recommendations(avg_sodium, limit)
    }

@router.get("/daily-log/{user_id}", response_model=DailySodiumLog)
async def get_daily_log(
    user_id: str,
    date: str = None,  # query param, defaults to today
    db: AsyncSession = Depends(get_db)
):
    return await get_daily_sodium(user_id, date, db)

class SodiumLimitRequest(BaseModel):
    limit_mg: int

@router.patch("/sodium-limit/{user_id}", response_model=SodiumLimitUpdate)
async def update_sodium_limit(
    user_id: str,
    request: SodiumLimitRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await update_user_sodium_limit(user_id, request.limit_mg, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/ingredient-alert/{recipe_id}")
async def get_ingredient_alert(
    recipe_id: str,
    db: AsyncSession = Depends(get_db)
):
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    parsed = recipe.parsed_json or {}
    ingredients = parsed.get("ingredients", []) if isinstance(parsed, dict) else []
    breakdown = calculate_ingredient_breakdown(ingredients)

    alerts = []
    for ing in breakdown["ingredients"]:
        if ing["sodium_mg"] > 500:
            alerts.append({
                "ingredient": ing["name"],
                "sodium_mg": ing["sodium_mg"],
                "alert": f"{ing['name']} contributes {round(ing['sodium_mg'])}mg sodium — consider reducing or omitting raw salt entirely"
            })

    return {
        "recipe_id": recipe_id,
        "recipe_title": recipe.title,
        "has_high_sodium_ingredients": len(alerts) > 0,
        "alerts": alerts,
        "total_hidden_sodium_mg": breakdown["total_hidden_sodium_mg"]
    }
