import pytest
from app.services.rescue_service import classify_severity, get_rescue_strategies

def test_severity_mild():
    assert classify_severity(12.0, 10.0) == "mild"

def test_severity_moderate():
    assert classify_severity(15.0, 10.0) == "moderate"

def test_severity_severe():
    assert classify_severity(20.0, 10.0) == "severe"

def test_severity_none():
    assert classify_severity(10.5, 10.0) == "none"

def test_rescue_returns_strategies():
    result = get_rescue_strategies("soup", 15.0, 10.0, 4, 1000)
    assert result["severity"] == "moderate"
    assert len(result["strategies"]) == 2
    assert result["excess_salt_grams"] == 5.0

def test_rescue_severe_returns_all():
    result = get_rescue_strategies("meat", 25.0, 10.0, 4, 800)
    assert result["severity"] == "severe"
    assert len(result["strategies"]) >= 2

def test_rescue_not_oversalted():
    result = get_rescue_strategies("soup", 10.0, 10.0, 4, 1000)
    assert result["severity"] == "none"
    assert result["strategies"] == []

def test_unknown_dish_type_fallback():
    result = get_rescue_strategies("stew", 20.0, 10.0, 4, 800)
    assert len(result["strategies"]) > 0  # falls back to "other"
