import pytest
from app.agents.culinary_analyst import calculate_hidden_sodium, calculate_baseline_salt

def test_calculate_hidden_sodium():
    ingredients = [
        {"name": "soy sauce", "amount": 2, "unit": "tbsp"},
        {"name": "chicken breast", "amount": 500, "unit": "g"}
    ]
    sodium, sources = calculate_hidden_sodium(ingredients)
    
    assert sodium > 1000
    assert "soy sauce" in sources

def test_calculate_baseline_salt():
    baseline = calculate_baseline_salt(
        total_mass_grams=1000.0, 
        dish_type="soup", 
        cooking_method="simmer", 
        evaporation_factor=1.0
    )
    
    assert 8 <= baseline <= 15
