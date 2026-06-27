import pytest
from app.services.user_service import get_user_sodium_limit

@pytest.mark.asyncio
async def test_get_user_sodium_limit_default():
    """No user record returns AHA default"""
    from unittest.mock import AsyncMock
    mock_db = AsyncMock()
    mock_db.get.return_value = None
    result = await get_user_sodium_limit("nonexistent", mock_db)
    assert result == 2300

@pytest.mark.asyncio
async def test_get_user_sodium_limit_custom():
    """User with custom limit returns their limit"""
    from unittest.mock import AsyncMock, MagicMock
    mock_db = AsyncMock()
    mock_user = MagicMock()
    mock_user.sodium_daily_limit_mg = 1500
    mock_db.get.return_value = mock_user
    result = await get_user_sodium_limit("user123", mock_db)
    assert result == 1500

def test_pipeline_state_has_sodium_limit_field():
    from app.agents.state import RecipePipelineState
    import typing
    hints = typing.get_type_hints(RecipePipelineState)
    assert "user_sodium_limit_mg" in hints
