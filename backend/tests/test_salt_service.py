import pytest
from app.services.salt_service import convert_salt, get_all_conversion_ratios

def test_diamond_to_morton():
    result = convert_salt("Diamond Crystal Kosher", "Morton Kosher", 10.0)
    # Morton has more sodium per gram so you need less of it
    assert result["converted_grams"] < 10.0
    assert result["sodium_mg"] > 0

def test_sodium_preserved():
    # Sodium content must be identical in both salts after conversion
    result = convert_salt("Table Salt", "Fine Sea Salt", 5.0)
    from_sodium = 5.0 * 1000 * 0.393
    assert abs(result["sodium_mg"] - from_sodium) < 0.1

def test_same_salt_conversion():
    result = convert_salt("Diamond Crystal Kosher", "Diamond Crystal Kosher", 8.0)
    assert result["converted_grams"] == 8.0

def test_invalid_salt_raises():
    with pytest.raises(ValueError):
        convert_salt("Himalayan Pink", "Table Salt", 5.0)

def test_all_conversions_length():
    results = get_all_conversion_ratios("Diamond Crystal Kosher", 10.0)
    assert len(results) == 4  # all other 4 salt types
