from app.services.sodium_breakdown_service import calculate_ingredient_breakdown, get_sodium_percentage_breakdown

def test_breakdown_detects_miso():
    ingredients = [
        {"name": "miso paste", "amount": 3, "unit": "tbsp", "is_salty": True},
        {"name": "carrots", "amount": 2, "unit": "pcs", "is_salty": False}
    ]
    result = calculate_ingredient_breakdown(ingredients)
    assert result["total_hidden_sodium_mg"] > 1000
    assert result["highest_sodium_ingredient"] == "miso paste"
    assert result["ingredient_count"] >= 1

def test_breakdown_clean_recipe():
    """Recipe with no salty ingredients returns zero hidden sodium"""
    ingredients = [
        {"name": "carrots", "amount": 500, "unit": "g", "is_salty": False},
        {"name": "olive oil", "amount": 2, "unit": "tbsp", "is_salty": False}
    ]
    result = calculate_ingredient_breakdown(ingredients)
    assert result["total_hidden_sodium_mg"] == 0.0

def test_percentage_breakdown_sums_to_100():
    breakdown = {
        "ingredients": [
            {"name": "soy sauce", "sodium_mg": 1600, "is_primary_salt": False},
            {"name": "miso", "sodium_mg": 400, "is_primary_salt": False},
        ]
    }
    result = get_sodium_percentage_breakdown(breakdown, 2000.0)
    total_percent = sum(item["percent_of_total"] for item in result)
    assert abs(total_percent - 100.0) < 0.1

def test_percentage_breakdown_sorted():
    breakdown = {
        "ingredients": [
            {"name": "miso", "sodium_mg": 400, "is_primary_salt": False},
            {"name": "soy sauce", "sodium_mg": 1600, "is_primary_salt": False},
        ]
    }
    result = get_sodium_percentage_breakdown(breakdown, 2000.0)
    assert result[0]["name"] == "soy sauce"  # highest first
