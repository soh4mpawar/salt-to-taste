import os
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.palate_profile import PalateProfile

def update_dish_context(current: dict, dish_type: str, rating: str) -> dict:
    key = f"{dish_type}_{rating}"
    updated = dict(current) if current else {}
    updated[key] = updated.get(key, 0) + 1
    return updated

async def get_or_create_palate_profile(user_id: str, db: AsyncSession) -> PalateProfile:
    # Convert string to UUID if possible
    try:
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) and "-" in user_id else user_id
    except ValueError:
        user_uuid = user_id
        
    result = await db.execute(select(PalateProfile).where(PalateProfile.user_id == user_uuid))
    profile = result.scalars().first()
    
    if not profile:
        profile = PalateProfile(
            user_id=user_uuid,
            weights_json={},
            dish_context_weights={},
            total_feedback_count=0
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        
    return profile

async def update_palate_profile_after_feedback(
    user_id: str, 
    rating: str, 
    dish_type: str, 
    cooking_method: str, 
    feedback_count: int, 
    db: AsyncSession
) -> PalateProfile:
    profile = await get_or_create_palate_profile(user_id, db)
    
    profile.total_feedback_count = feedback_count
    profile.last_updated = datetime.now(timezone.utc)
    
    current = profile.dish_context_weights or {}
    profile.dish_context_weights = update_dish_context(current, dish_type, rating)
    
    await db.commit()
    await db.refresh(profile)
    return profile

async def get_palate_summary(user_id: str, db: AsyncSession) -> dict:
    profile = await get_or_create_palate_profile(user_id, db)
    
    return {
        "user_id": str(user_id),
        "total_feedback_count": profile.total_feedback_count,
        "dish_preferences": profile.dish_context_weights,
        "model_trained": os.path.exists(f"models/{user_id}.vw"),
        "last_updated": profile.last_updated.isoformat() if profile.last_updated else None
    }
