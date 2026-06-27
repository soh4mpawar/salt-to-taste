import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.services.palate_service import update_dish_context, get_palate_summary
from app.models.palate_profile import PalateProfile

def test_update_dish_context():
    current = {"pasta_too_salty": 1}
    updated = update_dish_context(current, "pasta", "perfect")
    assert updated == {"pasta_too_salty": 1, "pasta_perfect": 1}
    
    updated2 = update_dish_context(updated, "pasta", "perfect")
    assert updated2 == {"pasta_too_salty": 1, "pasta_perfect": 2}
    
    # Test with empty current
    updated_empty = update_dish_context({}, "soup", "needs_more")
    assert updated_empty == {"soup_needs_more": 1}

@pytest.mark.asyncio
async def test_get_palate_summary():
    mock_db = AsyncMock()
    
    # Create mock result chain for db.execute().scalars().first()
    mock_result = MagicMock()
    mock_profile = PalateProfile(
        user_id="12345678-1234-5678-1234-567812345678",
        weights_json={},
        dish_context_weights={"pasta_perfect": 2},
        total_feedback_count=5,
        last_updated=datetime(2026, 1, 1, 12, 0, 0)
    )
    mock_result.scalars.return_value.first.return_value = mock_profile
    mock_db.execute.return_value = mock_result
    
    summary = await get_palate_summary("12345678-1234-5678-1234-567812345678", mock_db)
    
    assert summary["user_id"] == "12345678-1234-5678-1234-567812345678"
    assert summary["total_feedback_count"] == 5
    assert summary["dish_preferences"] == {"pasta_perfect": 2}
    assert summary["last_updated"] == "2026-01-01T12:00:00"
    assert "model_trained" in summary
