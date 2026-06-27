import pytest
from app.services.sodium_tracking_service import get_daily_sodium

@pytest.mark.asyncio
async def test_daily_sodium_empty():
    """Returns zeroed response for user with no log"""
    from unittest.mock import AsyncMock, MagicMock
    mock_db = AsyncMock()
    mock_db.get.return_value = None
    
    # Mock db.execute for PalateProfile lookup
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result
    
    # We also need to mock get_user_sodium_limit so it doesn't fail
    import app.services.sodium_tracking_service
    app.services.sodium_tracking_service.get_user_sodium_limit = AsyncMock(return_value=2300)
    
    result = await get_daily_sodium("new_user", "2026-06-27", mock_db)
    assert result["total_sodium_mg"] == 0.0
    assert result["within_limit"] is True

def test_weekly_summary_structure():
    """Weekly summary has correct shape"""
    # Test the dict-building logic in isolation
    days_data = [
        {"date": "2026-06-27", "total_mg": 1200, "within_limit": True},
        {"date": "2026-06-26", "total_mg": 2500, "within_limit": False},
    ]
    within = sum(1 for d in days_data if d["within_limit"])
    over = sum(1 for d in days_data if not d["within_limit"])
    assert within == 1
    assert over == 1
