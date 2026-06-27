import pytest
from app.services.scaling_service import scale_recipe, scale_ingredients, calculate_scaled_sodium

def test_scaling_up_sub_linear():
    result = scale_recipe(4, 8, 10.0, "soup")
    # Should be less than 20.0 (linear) due to sub-linear scaling
    assert result["scaled_salt_grams"] < 20.0
    assert result["scaled_salt_grams"] > 10.0  # but more than original

def test_scaling_down():
    result = scale_recipe(4, 2, 10.0, "soup")
    assert result["scaled_salt_grams"] < 10.0

def test_scaling_same_servings():
    result = scale_recipe(4, 4, 10.0, "pasta")
    assert result["scaled_salt_grams"] == 10.0

def test_bread_most_sublinear():
    bread = scale_recipe(4, 8, 10.0, "bread")
    pasta = scale_recipe(4, 8, 10.0, "pasta")
    # Bread should scale less aggressively than pasta
    assert bread["scaled_salt_grams"] < pasta["scaled_salt_grams"]

def test_scale_ingredients_linear():
    ingredients = [{"name": "carrots", "amount": 4, "unit": "pcs"}]
    result = scale_ingredients(ingredients, 4, 8)
    assert result[0]["amount"] == 8.0

def test_sodium_calculation():
    result = calculate_scaled_sodium(10.0, "Diamond Crystal Kosher", 4)
    assert result["total_sodium_mg"] == pytest.approx(3930.0, rel=0.01)
    assert result["sodium_mg_per_serving"] == pytest.approx(982.5, rel=0.01)

def test_invalid_servings():
    with pytest.raises(ValueError):
        scale_recipe(4, 0, 10.0, "soup")

def test_invalid_servings_too_large():
    with pytest.raises(ValueError):
        scale_recipe(4, 101, 10.0, "soup")
