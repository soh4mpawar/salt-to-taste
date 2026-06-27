from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.graphs.recipe_pipeline import run_recipe_pipeline
from app.models.recipe import Recipe
from app.models.recipe_salt_recommendation import RecipeSaltRecommendation
from app.models.salt_type import SaltType
from app.schemas.recommendation import RecommendationRead

async def process_recipe(
    raw_input: str,
    input_type: str,
    user_id: UUID,
    db: AsyncSession,
    image_bytes: bytes = None,
    low_sodium_mode: bool = False
) -> dict:
    from app.services.user_service import get_user_sodium_limit, get_user_low_sodium_preference
    user_id_str = str(user_id)
    
    user_limit = await get_user_sodium_limit(user_id_str, db)
    user_pref = await get_user_low_sodium_preference(user_id_str, db)
    effective_low_sodium_mode = low_sodium_mode or user_pref
    
    result = await run_recipe_pipeline(raw_input, input_type, user_id_str, image_bytes=image_bytes, low_sodium_mode=effective_low_sodium_mode, user_sodium_limit_mg=user_limit)
    
    if result.get("parsing_error") or result.get("pipeline_stage") == "parsing_failed":
        raise HTTPException(status_code=422, detail=f"Could not parse recipe: {result.get('parsing_error')}")
        
    if result.get("analysis_error"):
        raise HTTPException(status_code=422, detail=f"Analysis failed: {result.get('analysis_error')}")

    recipe = Recipe(
        user_id=user_id,
        title=result.get("recipe_title") or "Untitled Recipe",
        source_url=raw_input if input_type == "url" else None,
        source_type=input_type,
        raw_content=raw_input,
        parsed_json=result.get("parsed_recipe", {}),
        total_mass_grams=result.get("total_mass_grams"),
        servings=result.get("servings")
    )
    db.add(recipe)
    await db.flush() 
    
    salt_name = result.get("recommended_salt_type", "Diamond Crystal Kosher")
    stmt = select(SaltType).where(SaltType.name == salt_name)
    salt_result = await db.execute(stmt)
    salt_type = salt_result.scalars().first()
    
    if not salt_type:
        salt_type_id = 1
        salt_type_name = "Diamond Crystal Kosher"
    else:
        salt_type_id = salt_type.id
        salt_type_name = salt_type.name

    recommendation = RecipeSaltRecommendation(
        recipe_id=recipe.id,
        user_id=user_id,
        salt_type_id=salt_type_id,
        baseline_grams=result.get("baseline_salt_grams", 0.0),
        personalized_grams=result.get("personalized_salt_grams", 0.0),
        sodium_mg_per_serving=result.get("sodium_mg_per_serving", 0.0),
        recommendation_context=result.get("recommendation_context", {})
    )
    db.add(recommendation)
    await db.commit()
    await db.refresh(recommendation)

    # Auto-log sodium consumption after successful recommendation
    from app.services.sodium_tracking_service import log_sodium_consumed
    try:
        await log_sodium_consumed(
            user_id=user_id_str,
            recommendation_id=str(recommendation.id),
            sodium_mg_per_serving=float(recommendation.sodium_mg_per_serving),
            servings_eaten=1,  # default to 1 serving eaten
            db=db
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to auto-log sodium for recommendation {recommendation.id}: {e}")

    return {
        "id": recommendation.id,
        "recipe_id": recommendation.recipe_id,
        "user_id": recommendation.user_id,
        "salt_type_id": recommendation.salt_type_id,
        "salt_type_name": salt_type_name,
        "baseline_grams": recommendation.baseline_grams,
        "personalized_grams": recommendation.personalized_grams,
        "sodium_mg_per_serving": recommendation.sodium_mg_per_serving,
        "recommendation_context": recommendation.recommendation_context,
        "created_at": recommendation.created_at,
        "extraction_method": result.get("extraction_method"),
        "ocr_confidence": result.get("parsed_recipe", {}).get("ocr_confidence") if isinstance(result.get("parsed_recipe"), dict) else None,
        "low_sodium_warning": result.get("low_sodium_warning"),
        "herb_suggestions": result.get("herb_suggestions")
    }
