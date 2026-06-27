import pytest
import asyncio
import tempfile
from app.agents.personalization_engine import build_vw_features, get_palate_adjustment, PalateModelManager

def test_build_vw_features():
    feat = build_vw_features(dish_type="soup", cooking_method="simmer", baseline_grams=10.0, servings=2)
    assert "|dish" in feat
    assert "dish_type=soup" in feat
    assert "|method" in feat
    assert "cooking_method=simmer" in feat
    assert "baseline_norm=5.0" in feat

@pytest.mark.asyncio
async def test_get_palate_adjustment_no_model():
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = PalateModelManager(temp_dir)
        adj = await get_palate_adjustment(
            user_id="fake_user",
            dish_type="soup",
            cooking_method="simmer",
            baseline_grams=10.0,
            servings=4,
            model_manager=manager
        )
        assert adj == (1.0, 2)
