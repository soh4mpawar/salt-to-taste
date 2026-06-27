RESCUE_STRATEGIES = {
    "soup": [
        {
            "strategy": "dilution",
            "action": "Add more unsalted liquid",
            "detail": "Add {amount}ml of unsalted water, stock, or cream to dilute sodium concentration",
            "scales_with": "volume",
            "effectiveness": "high"
        },
        {
            "strategy": "bulk",
            "action": "Add more vegetables",
            "detail": "Add unsalted diced potato, carrot, or celery to absorb excess salt",
            "scales_with": "none",
            "effectiveness": "medium"
        },
        {
            "strategy": "acid",
            "action": "Add acid",
            "detail": "Add {amount} tsp of lemon juice or white wine vinegar to balance perception of saltiness",
            "scales_with": "servings",
            "effectiveness": "medium"
        },
    ],
    "meat": [
        {
            "strategy": "acid",
            "action": "Deglaze with acid",
            "detail": "Add {amount}ml white wine or {amount2} tbsp lemon juice to the pan to balance salt",
            "scales_with": "volume",
            "effectiveness": "high"
        },
        {
            "strategy": "fat",
            "action": "Add unsalted fat",
            "detail": "Add {amount} tbsp unsalted butter or cream to coat the palate and reduce salt perception",
            "scales_with": "servings",
            "effectiveness": "medium"
        },
    ],
    "roasted_vegetables": [
        {
            "strategy": "acid",
            "action": "Finish with acid",
            "detail": "Squeeze {amount} lemon(s) over the finished dish to counterbalance the salt",
            "scales_with": "servings",
            "effectiveness": "high"
        },
        {
            "strategy": "fat",
            "action": "Add unsalted fat",
            "detail": "Toss with {amount} tbsp of good olive oil or unsalted butter before serving",
            "scales_with": "servings",
            "effectiveness": "medium"
        },
        {
            "strategy": "bulk",
            "action": "Add unsalted vegetables",
            "detail": "Add more unsalted roasted vegetables to dilute the salt ratio",
            "scales_with": "none",
            "effectiveness": "medium"
        },
    ],
    "pasta": [
        {
            "strategy": "dilution",
            "action": "Add unsalted pasta water",
            "detail": "Reserve {amount}ml pasta water before draining and add to sauce to dilute",
            "scales_with": "volume",
            "effectiveness": "high"
        },
        {
            "strategy": "fat",
            "action": "Add unsalted fat",
            "detail": "Add {amount} tbsp unsalted butter or mascarpone to coat pasta and reduce salt perception",
            "scales_with": "servings",
            "effectiveness": "medium"
        },
    ],
    "salad": [
        {
            "strategy": "bulk",
            "action": "Add more unsalted greens",
            "detail": "Add extra unsalted greens, cucumber, or avocado to dilute dressing salt",
            "scales_with": "none",
            "effectiveness": "high"
        },
        {
            "strategy": "acid",
            "action": "Add sweetness",
            "detail": "Add {amount} tsp honey or a few raisins to counterbalance salt in the dressing",
            "scales_with": "servings",
            "effectiveness": "medium"
        },
    ],
    "seafood": [
        {
            "strategy": "acid",
            "action": "Finish with citrus",
            "detail": "Squeeze {amount} lemon(s) or lime(s) over the dish immediately before serving",
            "scales_with": "servings",
            "effectiveness": "high"
        },
        {
            "strategy": "fat",
            "action": "Add unsalted cream",
            "detail": "Add {amount} tbsp heavy cream or coconut cream to build a sauce that reduces salt perception",
            "scales_with": "servings",
            "effectiveness": "medium"
        },
    ],
    "other": [
        {
            "strategy": "acid",
            "action": "Add acid",
            "detail": "Add a small amount of lemon juice or vinegar to balance salt perception",
            "scales_with": "none",
            "effectiveness": "medium"
        },
        {
            "strategy": "fat",
            "action": "Add unsalted fat",
            "detail": "Add unsalted butter, cream, or oil to coat the palate",
            "scales_with": "none",
            "effectiveness": "medium"
        },
        {
            "strategy": "bulk",
            "action": "Add unsalted bulk",
            "detail": "Add more of the main unsalted ingredient to dilute the salt ratio",
            "scales_with": "none",
            "effectiveness": "low"
        },
    ]
}

SEVERITY_THRESHOLDS = {
    "mild": (1.1, 1.3),
    "moderate": (1.3, 1.6),
    "severe": (1.6, 999.0),
}

def classify_severity(actual_grams: float, target_grams: float) -> str:
    ratio = actual_grams / max(target_grams, 0.1)
    if ratio <= 1.1:
        return "none"
        
    if ratio < 1.3:
        return "mild"
    elif ratio < 1.6:
        return "moderate"
    else:
        return "severe"

def fill_strategy_amounts(strategy: dict, servings: int, total_mass_grams: float) -> dict:
    import copy
    filled = copy.deepcopy(strategy)
    scales = filled.get("scales_with", "none")
    
    if scales == "volume":
        amount = round(total_mass_grams * 0.15)
    elif scales == "servings":
        amount = max(1, round(servings / 2))
    else:
        amount = 1
        
    amount2 = amount // 2
    
    filled["detail"] = filled["detail"].replace("{amount}", str(amount))
    if "{amount2}" in filled["detail"]:
        filled["detail"] = filled["detail"].replace("{amount2}", str(amount2))
        
    return filled

def get_rescue_strategies(dish_type: str, actual_grams: float, target_grams: float, servings: int, total_mass_grams: float) -> dict:
    severity = classify_severity(actual_grams, target_grams)
    if severity == "none":
        return {"message": "Dish is not over-salted", "severity": "none", "strategies": []}
        
    strategies = RESCUE_STRATEGIES.get(dish_type, RESCUE_STRATEGIES["other"])
    
    order = {"high": 3, "medium": 2, "low": 1}
    sorted_strategies = sorted(strategies, key=lambda s: order.get(s.get("effectiveness", "low"), 0), reverse=True)
    
    if severity == "severe":
        selected = sorted_strategies
    elif severity == "moderate":
        selected = sorted_strategies[:2]
    else:
        selected = sorted_strategies[:1]
        
    filled_strategies = [fill_strategy_amounts(s, servings, total_mass_grams) for s in selected]
    
    return {
        "severity": severity,
        "dish_type": dish_type,
        "excess_salt_grams": round(actual_grams - target_grams, 2),
        "strategies": filled_strategies,
        "primary_recommendation": filled_strategies[0]["action"] if filled_strategies else None
    }
