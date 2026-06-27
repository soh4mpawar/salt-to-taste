from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.schemas.recipe import RecipeCreate, RecipeImageUploadResponse
from app.schemas.recommendation import RecommendationRead
from app.utils.image_processing import validate_image_format
from app.services.recipe_service import process_recipe
from app.models.user import User
from app.core.config import settings
from app.schemas.health import SodiumBreakdownResponse

router = APIRouter()

@router.post(
    "",
    status_code=201,
    summary="Submit a recipe from text or URL",
    description="Runs the full LangGraph pipeline: parsing → culinary analysis → personalization.",
    response_model=RecommendationRead
)
async def create_recipe(recipe_in: RecipeCreate, db: AsyncSession = Depends(get_db)):
    # Use user_id from request body if provided, otherwise fall back
    user_id_str = recipe_in.user_id or "14cc53c8-c2be-44c3-abeb-b175d6859d25"
    try:
        user_uuid = UUID(user_id_str)
    except ValueError:
        user_uuid = UUID("14cc53c8-c2be-44c3-abeb-b175d6859d25")

    user = await db.get(User, user_uuid)
    
    if not user:
        user = User(id=user_uuid, email="test@example.com", display_name="Test User")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return await process_recipe(
        raw_input=recipe_in.raw_content,
        input_type=recipe_in.source_type.value,
        user_id=user.id,
        low_sodium_mode=recipe_in.low_sodium_mode,
        db=db
    )

@router.post(
    "/image-upload",
    status_code=201,
    summary="Submit a recipe from a cookbook image or photo",
    description="Accepts JPEG, PNG, WEBP, or PDF (first page only). Automatically selects Tesseract or vision LLM based on image quality.",
    response_model=RecipeImageUploadResponse
)
async def upload_recipe_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    image_bytes = await file.read()
    
    if len(image_bytes) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large (max {settings.MAX_UPLOAD_SIZE_MB}MB)")
        
    valid, reason = validate_image_format(image_bytes, file.filename)
    if not valid:
        raise HTTPException(status_code=415, detail=f"Unsupported format: {reason}")
        
    # Make sure user exists since FK is enforced
    user_uuid = UUID(user_id) if "-" in user_id else UUID("00000000-0000-0000-0000-000000000001")
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalars().first()
    if not user:
        user = User(id=user_uuid, email="test_upload@example.com", display_name="Test Upload")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return await process_recipe(
        raw_input=file.filename,
        input_type="image",
        user_id=user.id,
        db=db,
        image_bytes=image_bytes
    )

@router.get("/{recipe_id}")
async def get_recipe(recipe_id: UUID):
    return {"status": "not_implemented", "endpoint": "GET /recipes/{recipe_id}"}

@router.get("")
async def list_recipes():
    return {"status": "not_implemented", "endpoint": "GET /recipes"}

@router.get("/{recipe_id}/sodium-breakdown", response_model=SodiumBreakdownResponse)
async def get_sodium_breakdown(
    recipe_id: str,
    db: AsyncSession = Depends(get_db)
):
    from app.models.recipe import Recipe
    from app.models.recipe_salt_recommendation import RecipeSaltRecommendation
    from app.services.sodium_breakdown_service import calculate_ingredient_breakdown, get_sodium_percentage_breakdown
    
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    parsed = recipe.parsed_json or {}
    ingredients = parsed.get("ingredients", []) if isinstance(parsed, dict) else []

    breakdown = calculate_ingredient_breakdown(ingredients)

    # Get latest recommendation for total sodium context
    result = await db.execute(
        select(RecipeSaltRecommendation)
        .where(RecipeSaltRecommendation.recipe_id == recipe_id)
        .order_by(RecipeSaltRecommendation.created_at.desc())
        .limit(1)
    )
    recommendation = result.scalar_one_or_none()
    total_sodium = float(recommendation.sodium_mg_per_serving) if recommendation else 0.0

    percentage_breakdown = get_sodium_percentage_breakdown(breakdown, total_sodium)

    return {
        **breakdown,
        "sodium_per_serving_mg": total_sodium,
        "percentage_breakdown": percentage_breakdown,
        "recipe_id": recipe_id,
        "recipe_title": recipe.title
    }

@router.post("/{recipe_id}/scale")
async def scale_recipe_endpoint(
    recipe_id: str,
    target_servings: int,
    db: AsyncSession = Depends(get_db)
):
    from app.models.recipe import Recipe
    from app.models.recipe_salt_recommendation import RecipeSaltRecommendation
    from app.services.scaling_service import scale_recipe, scale_ingredients, calculate_scaled_sodium
    
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Get most recent recommendation for this recipe
    result = await db.execute(
        select(RecipeSaltRecommendation)
        .where(RecipeSaltRecommendation.recipe_id == recipe_id)
        .order_by(RecipeSaltRecommendation.created_at.desc())
        .limit(1)
    )
    recommendation = result.scalar_one_or_none()
    if not recommendation:
        raise HTTPException(status_code=404, detail="No recommendation found for this recipe")

    context = recommendation.recommendation_context or {}
    dish_type = context.get("dish_type", "other")
    SALT_ID_TO_NAME = {
        1: "Diamond Crystal Kosher",
        2: "Morton Kosher",
        3: "Fine Sea Salt",
        4: "Table Salt",
        5: "Maldon Flake",
    }
    salt_type = SALT_ID_TO_NAME.get(recommendation.salt_type_id, "Diamond Crystal Kosher")

    scaling_result = scale_recipe(
        original_servings=recipe.servings or 4,
        target_servings=target_servings,
        original_salt_grams=float(recommendation.personalized_grams),
        dish_type=dish_type
    )

    parsed = recipe.parsed_json or {}
    ingredients = parsed.get("ingredients", []) if isinstance(parsed, dict) else []
    scaled_ingredients = scale_ingredients(ingredients, recipe.servings or 4, target_servings)

    sodium_info = calculate_scaled_sodium(
        scaling_result["scaled_salt_grams"], salt_type, target_servings
    )

    return {
        **scaling_result,
        "scaled_ingredients": scaled_ingredients,
        "sodium_info": sodium_info,
        "salt_type": salt_type
    }
