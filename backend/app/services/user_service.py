from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

async def get_user_sodium_limit(user_id: str, db: AsyncSession) -> int:
    """Returns the user's daily sodium limit in mg. Falls back to AHA default."""
    from app.agents.personalization_engine import AHA_SODIUM_LIMIT_MG
    try:
        user = await db.get(User, user_id)
        if user and user.sodium_daily_limit_mg and user.sodium_daily_limit_mg > 0:
            return user.sodium_daily_limit_mg
    except Exception:
        pass
    return AHA_SODIUM_LIMIT_MG

async def get_user_low_sodium_preference(user_id: str, db: AsyncSession) -> bool:
    """Returns the user's low_sodium_mode preference from their profile."""
    try:
        user = await db.get(User, user_id)
        if user:
            return bool(user.low_sodium_mode)
    except Exception:
        pass
    return False

async def update_user_sodium_limit(user_id: str, limit_mg: int, db: AsyncSession) -> dict:
    """Updates a user's custom sodium limit."""
    user = await db.get(User, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    if limit_mg < 0 or limit_mg > 10000:
        raise ValueError("Sodium limit must be between 0 and 10000mg")
    user.sodium_daily_limit_mg = limit_mg if limit_mg > 0 else None
    await db.commit()
    return {"user_id": user_id, "sodium_daily_limit_mg": limit_mg, "updated": True}
