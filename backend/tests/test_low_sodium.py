import pytest
from app.agents.personalization_engine import get_herb_suggestions

def test_herb_suggestions_by_dish():
    result = get_herb_suggestions("soup")
    assert len(result) >= 2
    assert isinstance(result[0], str)

def test_herb_suggestions_fallback():
    result = get_herb_suggestions("unknown_dish")
    assert len(result) > 0

def test_aha_limit_constant():
    from app.agents.personalization_engine import AHA_SODIUM_LIMIT_MG
    assert AHA_SODIUM_LIMIT_MG == 2300
