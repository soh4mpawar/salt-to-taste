import json
from app.agents.state import RecipePipelineState
from app.core.ollama import get_analysis_llm

HIDDEN_SODIUM_SOURCES = {
    "soy sauce": 5493,
    "fish sauce": 5764,
    "miso": 3728,
    "worcestershire": 3100,
    "canned tomatoes": 220,
    "chicken broth": 420,
    "beef broth": 372,
    "vegetable broth": 350,
    "parmesan": 1529,
    "feta": 1116,
    "olives": 735,
    "capers": 2964,
    "anchovies": 3668,
    "bacon": 1717,
    "sausage": 1200,
    "pickles": 1208,
    "kimchi": 498,
    "tahini": 115,
    "mustard": 1120,
}

UNIT_TO_GRAMS = {
    "cup": 240,
    "cups": 240,
    "tbsp": 15,
    "tablespoon": 15,
    "tablespoons": 15,
    "tsp": 5,
    "teaspoon": 5,
    "teaspoons": 5,
    "oz": 28,
    "ounce": 28,
    "ounces": 28,
    "g": 1,
    "gram": 1,
    "grams": 1,
    "ml": 1,
    "milliliter": 1,
    "milliliters": 1,
    "l": 1000,
    "liter": 1000,
    "liters": 1000,
    "kg": 1000,
    "kilogram": 1000,
    "kilograms": 1000,
    "lb": 454,
    "lbs": 454,
    "pound": 454,
    "pounds": 454,
}

def calculate_hidden_sodium(ingredients: list) -> tuple[float, list]:
    total_hidden_sodium_mg = 0.0
    detected_sources = []
    
    for ing in ingredients:
        name = ing.get("name", "").lower()
        amount = float(ing.get("amount", 0))
        unit = ing.get("unit", "").lower()
        
        grams = amount * UNIT_TO_GRAMS.get(unit, 1.0)
        
        for source, sodium_per_100g in HIDDEN_SODIUM_SOURCES.items():
            if source in name:
                sodium = (grams * sodium_per_100g) / 100.0
                total_hidden_sodium_mg += sodium
                if source not in detected_sources:
                    detected_sources.append(source)
                break
                
    return total_hidden_sodium_mg, detected_sources

BASE_RATIOS = {
    "soup": 0.010,
    "pasta": 0.010,
    "meat": 0.012,
    "roasted_vegetables": 0.015,
    "salad": 0.008,
    "seafood": 0.009,
    "bread": 0.018,
    "other": 0.011,
}

COOKING_METHOD_MULTIPLIERS = {
    "simmer": 1.15,
    "roast": 1.10,
    "bake": 1.0,
    "fry": 0.95,
    "steam": 1.0,
    "raw": 0.90,
    "grill": 1.05,
}

def calculate_baseline_salt(total_mass_grams: float, dish_type: str, cooking_method: str, evaporation_factor: float) -> float:
    base_ratio = BASE_RATIOS.get(dish_type, BASE_RATIOS["other"])
    method_multiplier = COOKING_METHOD_MULTIPLIERS.get(cooking_method, 1.0)
    baseline = total_mass_grams * base_ratio * method_multiplier * evaporation_factor
    return baseline

def build_analysis_prompt(parsed_recipe: dict) -> str:
    recipe_json_str = json.dumps(parsed_recipe, indent=2)
    return f"""You are a culinary analyst.
Estimate the total cooked mass in grams of the entire dish.
Identify the primary dish type from the allowed list: soup, pasta, meat, roasted_vegetables, salad, seafood, bread, other.
Identify the primary cooking method from the allowed list: simmer, roast, bake, fry, steam, raw, grill.
Estimate the evaporation factor (1.0 = no evaporation, 1.3 = significant reduction).

Return ONLY JSON format exactly like this example:
{{
  "total_mass_grams": 800,
  "dish_type": "soup",
  "cooking_method": "simmer",
  "evaporation_factor": 1.2,
  "reasoning": "brief explanation"
}}

Recipe Data:
{recipe_json_str}
"""

async def culinary_analyst_node(state: RecipePipelineState) -> dict:
    if state.get("parsing_error"):
        return {"pipeline_stage": "analysis_skipped"}
        
    parsed_recipe = state.get("parsed_recipe", {})
    if not parsed_recipe:
        parsed_recipe = {
            "title": state.get("recipe_title"),
            "ingredients": state.get("ingredients", []),
            "steps": state.get("steps", []),
            "servings": state.get("servings")
        }
        
    prompt = build_analysis_prompt(parsed_recipe)
    llm = get_analysis_llm()
    
    try:
        response = await llm.ainvoke(prompt)
        response_text = response.content.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        analysis_data = json.loads(response_text.strip())
        
        def safe_float(val, default):
            try:
                return float(val) if val is not None else default
            except:
                return default
                
        total_mass = safe_float(analysis_data.get("total_mass_grams"), 1000.0)
        dish_type = str(analysis_data.get("dish_type") or "other")
        cooking_method = str(analysis_data.get("cooking_method") or "simmer")
        evaporation_factor = safe_float(analysis_data.get("evaporation_factor"), 1.0)
        
        ingredients = state.get("ingredients", [])
        if not ingredients and parsed_recipe.get("ingredients"):
            ingredients = parsed_recipe["ingredients"]
            
        hidden_sodium, detected_sources = calculate_hidden_sodium(ingredients)
        
        baseline_salt = calculate_baseline_salt(total_mass, dish_type, cooking_method, evaporation_factor)
        
        adjusted_baseline = baseline_salt - (hidden_sodium / 1000.0 * 2.5)
        adjusted_baseline = max(0.5, adjusted_baseline)
        
        return {
            "total_mass_grams": total_mass,
            "hidden_sodium_mg": hidden_sodium,
            "baseline_salt_grams": round(adjusted_baseline, 2),
            "dish_type": dish_type,
            "cooking_method": cooking_method,
            "evaporation_factor": evaporation_factor,
            "analysis_notes": f"Detected hidden sodium sources: {detected_sources}",
            "pipeline_stage": "analysis_complete"
        }
    except Exception as e:
        error_msg = str(e)
        return {
            "analysis_error": error_msg,
            "pipeline_stage": "analysis_failed",
            "errors": [error_msg]
        }
