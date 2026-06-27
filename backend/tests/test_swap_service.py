import pytest
from app.services.swap_service import calculate_ingredient_sodium, calculate_swap_adjustment

def test_soy_sauce_sodium():
    sodium, found = calculate_ingredient_sodium("soy sauce", 2, "tbsp")
    assert found is True
    assert sodium > 1000  # 2 tbsp soy sauce has ~1600mg sodium

def test_unknown_ingredient():
    sodium, found = calculate_ingredient_sodium("truffle oil", 1, "tbsp")
    assert found is False
    assert sodium == 0.0

def test_swap_adjustment_reduces_salt():
    result = calculate_swap_adjustment(1600.0, "Diamond Crystal Kosher")
    assert result["equivalent_salt_grams"] > 3.0  # 1600mg sodium = ~4g Diamond Crystal

def test_swap_adjustment_zero_sodium():
    result = calculate_swap_adjustment(0.0, "Diamond Crystal Kosher")
    assert result["equivalent_salt_grams"] == 0.0
