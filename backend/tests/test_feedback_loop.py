import pytest
import tempfile
import os
from app.agents.personalization_engine import (
    PalateModelManager,
    record_feedback,
    get_palate_adjustment
)

@pytest.mark.asyncio
async def test_bandit_learns_from_feedback():
    """
    Simulate a user who always finds food too salty.
    After enough feedback, the model should recommend action 1 (too_salty reduction).
    """
    # Use a temp directory so tests don't pollute the real models/ folder
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = PalateModelManager(model_dir=tmpdir)
        user_id = "test_learner_user"

        # Simulate 15 "too_salty" feedback entries for roasted_vegetables
        for i in range(15):
            success, count = await record_feedback(
                user_id=user_id,
                dish_type="roasted_vegetables",
                cooking_method="roast",
                baseline_grams=10.0,
                servings=4,
                rating="too_salty",
                model_manager=manager
            )
            assert success is True

        # After 15 consistent "too salty" signals, model should predict action 1
        multiplier, action = await get_palate_adjustment(
            user_id=user_id,
            dish_type="roasted_vegetables",
            cooking_method="roast",
            baseline_grams=10.0,
            servings=4,
            model_manager=manager
        )

        # The multiplier should be less than 1.0 — model learned to reduce salt
        assert multiplier < 1.0, f"Expected multiplier < 1.0 after too_salty feedback, got {multiplier}"
        assert action == 1, f"Expected action 1 (too_salty), got {action}"


@pytest.mark.asyncio
async def test_bandit_learns_perfect():
    """
    Simulate a user who always rates food as perfect.
    Model should converge to action 2 (no adjustment).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = PalateModelManager(model_dir=tmpdir)
        user_id = "test_perfect_user"

        for i in range(15):
            await record_feedback(
                user_id=user_id,
                dish_type="soup",
                cooking_method="simmer",
                baseline_grams=8.0,
                servings=6,
                rating="perfect",
                model_manager=manager
            )

        multiplier, action = await get_palate_adjustment(
            user_id=user_id,
            dish_type="soup",
            cooking_method="simmer",
            baseline_grams=8.0,
            servings=6,
            model_manager=manager
        )

        assert action == 2, f"Expected action 2 (perfect), got {action}"
        assert multiplier == 1.0


@pytest.mark.asyncio
async def test_new_user_returns_baseline():
    """New users with no model get multiplier 1.0"""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = PalateModelManager(model_dir=tmpdir)
        multiplier, action = await get_palate_adjustment(
            user_id="brand_new_user",
            dish_type="meat",
            cooking_method="grill",
            baseline_grams=12.0,
            servings=4,
            model_manager=manager
        )
        assert multiplier == 1.0
        assert action == 2
