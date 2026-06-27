from app.agents.culinary_analyst import HIDDEN_SODIUM_SOURCES, UNIT_TO_GRAMS

def calculate_ingredient_breakdown(ingredients: list[dict]) -> dict:
    ingredient_results = []
    total_hidden_sodium = 0.0
    highest_sodium = 0.0
    highest_name = None
    
    for ing in ingredients:
        name = ing.get("name", "").lower()
        amount = ing.get("amount", 0.0)
        unit = ing.get("unit", "").lower()
        is_salty = ing.get("is_salty", False)
        
        sodium_mg = 0.0
        source = None
        is_primary_salt = False
        
        # Check hidden sodium database
        matched_key = next((key for key in HIDDEN_SODIUM_SOURCES if key in name), None)
        
        if matched_key:
            grams = amount * UNIT_TO_GRAMS.get(unit, 100) # default to 100g if unit unknown
            sodium_mg = grams * (HIDDEN_SODIUM_SOURCES[matched_key] / 100)
            source = "hidden_sodium_db"
        elif "salt" in name and not is_salty:
            # Check for raw salt (not explicitly marked but has salt in name)
            # We assume it's table salt (approx 39.3% sodium)
            grams = amount * UNIT_TO_GRAMS.get(unit, 100)
            sodium_mg = grams * 0.393 * 1000  # 393mg per gram
            source = "raw_salt"
            is_primary_salt = True
            
        if sodium_mg > 0:
            total_hidden_sodium += sodium_mg
            ingredient_results.append({
                "name": ing.get("name", ""),
                "amount": amount,
                "unit": ing.get("unit", ""),
                "sodium_mg": round(sodium_mg, 1),
                "source": source,
                "is_primary_salt": is_primary_salt
            })
            
            if sodium_mg > highest_sodium:
                highest_sodium = sodium_mg
                highest_name = ing.get("name", "")
                
    return {
        "ingredients": ingredient_results,
        "total_hidden_sodium_mg": round(total_hidden_sodium, 1),
        "highest_sodium_ingredient": highest_name,
        "ingredient_count": len(ingredient_results)
    }

def get_sodium_percentage_breakdown(breakdown: dict, total_sodium_mg: float) -> list[dict]:
    if total_sodium_mg <= 0:
        return []
        
    percentages = []
    for ing in breakdown.get("ingredients", []):
        if ing.get("sodium_mg", 0) > 0:
            pct = (ing["sodium_mg"] / total_sodium_mg) * 100
            percentages.append({
                "name": ing["name"],
                "sodium_mg": ing["sodium_mg"],
                "percent_of_total": round(pct, 1)
            })
            
    percentages.sort(key=lambda x: x["sodium_mg"], reverse=True)
    return percentages
