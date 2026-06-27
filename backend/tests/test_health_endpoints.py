from app.api.health import _get_health_recommendations

def test_health_recommendations_high_sodium():
    result = _get_health_recommendations(1200.0, 2300)
    assert any("Low-Sodium Mode" in r for r in result)

def test_health_recommendations_normal():
    result = _get_health_recommendations(500.0, 2300)
    assert any("healthy" in r for r in result)

def test_health_recommendations_too_low():
    result = _get_health_recommendations(50.0, 2300)
    assert any("very low" in r for r in result)
