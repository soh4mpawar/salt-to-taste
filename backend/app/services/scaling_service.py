SALT_SCALING_EXPONENTS = {
    "soup": 0.85,
    "pasta": 0.90,
    "meat": 0.88,
    "roasted_vegetables": 0.92,
    "salad": 0.95,
    "seafood": 0.88,
    "bread": 0.80,   # bread is most sub-linear — yeast dynamics
    "other": 0.90,
}

def scale_recipe(original_servings: int, target_servings: int, original_salt_grams: float, dish_type: str) -> dict:
    if target_servings < 1 or target_servings > 100:
        raise ValueError("Target servings must be between 1 and 100")
        
    exponent = SALT_SCALING_EXPONENTS.get(dish_type, SALT_SCALING_EXPONENTS["other"])
    ratio = target_servings / max(1, original_servings)
    
    scaled_salt = original_salt_grams * (ratio ** exponent)
    linear_salt = original_salt_grams * ratio
    
    return {
        "original_servings": original_servings,
        "target_servings": target_servings,
        "original_salt_grams": round(original_salt_grams, 2),
        "scaled_salt_grams": round(scaled_salt, 2),
        "linear_salt_grams": round(linear_salt, 2),
        "salt_saved_grams": round(linear_salt - scaled_salt, 2),
        "scaling_ratio": round(ratio, 3),
        "dish_type": dish_type,
        "note": f"Salt scaled sub-linearly (exponent {exponent}) - taste and adjust near the end"
    }

def scale_ingredients(ingredients: list[dict], original_servings: int, target_servings: int) -> list[dict]:
    ratio = target_servings / max(1, original_servings)
    scaled = []
    import copy
    for ing in ingredients:
        ing_copy = copy.deepcopy(ing)
        amount = float(ing_copy.get("amount", 0.0))
        ing_copy["amount"] = amount * ratio
        scaled.append(ing_copy)
    return scaled

def calculate_scaled_sodium(scaled_salt_grams: float, salt_type_name: str, servings: int) -> dict:
    from app.services.salt_service import SALT_SODIUM_PERCENT, SALT_NAME_TO_KEY
    salt_key = SALT_NAME_TO_KEY.get(salt_type_name, "diamond_crystal_kosher")
    sodium_percent = SALT_SODIUM_PERCENT.get(salt_key, 0.393)
    
    total_sodium_mg = scaled_salt_grams * 1000 * sodium_percent
    sodium_per_serving = total_sodium_mg / max(1, servings)
    
    return {
        "total_sodium_mg": round(total_sodium_mg, 1),
        "sodium_mg_per_serving": round(sodium_per_serving, 1),
        "aha_daily_limit_mg": 2300,
        "percent_of_daily_limit": round(sodium_per_serving / 23.0, 1)
    }
