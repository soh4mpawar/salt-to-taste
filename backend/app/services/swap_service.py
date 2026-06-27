from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.recipe_salt_recommendation import RecipeSaltRecommendation
from app.agents.culinary_analyst import HIDDEN_SODIUM_SOURCES, UNIT_TO_GRAMS
from app.services.salt_service import SALT_SODIUM_PERCENT, SALT_DENSITY_G_PER_ML, SALT_NAME_TO_KEY

def calculate_ingredient_sodium(ingredient_name: str, amount: float, unit: str) -> tuple[float, bool]:
    ingredient_lower = ingredient_name.lower()
    
    sodium_per_100g = 0.0
    found = False
    for key, value in HIDDEN_SODIUM_SOURCES.items():
        if key in ingredient_lower:
            sodium_per_100g = value
            found = True
            break
            
    if not found:
        return 0.0, False
        
    unit_lower = unit.lower()
    multiplier = UNIT_TO_GRAMS.get(unit_lower, 100.0) # default to 100g if unit unknown
    
    grams = amount * multiplier
    sodium_mg = (grams / 100.0) * sodium_per_100g
    
    return sodium_mg, True

def calculate_swap_adjustment(added_sodium_mg: float, salt_type_name: str) -> dict:
    if salt_type_name not in SALT_NAME_TO_KEY:
        salt_type_name = "Diamond Crystal Kosher"
        
    salt_key = SALT_NAME_TO_KEY[salt_type_name]
    sodium_percent = SALT_SODIUM_PERCENT[salt_key]
    density_g_per_ml = SALT_DENSITY_G_PER_ML[salt_key]
    
    equivalent_salt_grams = added_sodium_mg / (1000 * sodium_percent)
    equivalent_salt_tsp = equivalent_salt_grams / (density_g_per_ml / 5)
    
    return {
        "added_sodium_mg": round(added_sodium_mg, 1),
        "equivalent_salt_grams": round(equivalent_salt_grams, 2),
        "equivalent_salt_tsp": round(equivalent_salt_tsp, 2),
        "recommendation": f"Reduce your {salt_type_name} addition by {round(equivalent_salt_grams, 2)}g ({round(equivalent_salt_tsp, 2)} tsp)"
    }

async def process_salty_swap(recommendation_id: str, ingredient_name: str, amount: float, unit: str, db: AsyncSession) -> dict:
    result = await db.execute(select(RecipeSaltRecommendation).where(RecipeSaltRecommendation.id == recommendation_id))
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    sodium_mg, found = calculate_ingredient_sodium(ingredient_name, amount, unit)
    
    if not found:
        return {
            "ingredient_name": ingredient_name,
            "added_sodium_mg": 0.0,
            "equivalent_salt_grams": 0.0,
            "original_recommendation_grams": recommendation.personalized_grams,
            "adjusted_grams": recommendation.personalized_grams,
            "adjustment_applied": False,
            "recommendation": "No adjustment needed.",
            "warning": "Ingredient not in sodium database"
        }
        
    SALT_ID_TO_NAME = {
        1: "Diamond Crystal Kosher",
        2: "Morton Kosher",
        3: "Fine Sea Salt",
        4: "Table Salt",
        5: "Maldon Flake",
    }
    salt_type_name = SALT_ID_TO_NAME.get(recommendation.salt_type_id, "Diamond Crystal Kosher")
    swap_data = calculate_swap_adjustment(sodium_mg, salt_type_name)
    equivalent_salt_grams = swap_data["equivalent_salt_grams"]
    
    adjusted_grams = max(0.0, recommendation.personalized_grams - equivalent_salt_grams)
    
    # Update DB
    original_grams = recommendation.personalized_grams
    recommendation.personalized_grams = adjusted_grams
    
    # Since SQLAlchemy dicts can be weird with mutation, create a new dict
    context = dict(recommendation.recommendation_context or {})
    context_list = context.get("salty_swap_applied", [])
    if not isinstance(context_list, list):
        context_list = [context_list] if context_list else []
        
    context_list.append({
        "ingredient": ingredient_name,
        "sodium_added_mg": sodium_mg
    })
    context["salty_swap_applied"] = context_list
    recommendation.recommendation_context = context
    
    await db.commit()
    
    return {
        "ingredient_name": ingredient_name,
        "added_sodium_mg": swap_data["added_sodium_mg"],
        "equivalent_salt_grams": swap_data["equivalent_salt_grams"],
        "original_recommendation_grams": original_grams,
        "adjusted_grams": adjusted_grams,
        "adjustment_applied": True,
        "recommendation": swap_data["recommendation"],
        "warning": None
    }
