from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from app.models.palate_profile import PalateProfile
from app.services.user_service import get_user_sodium_limit

async def log_sodium_consumed(user_id: str, recommendation_id: str, sodium_mg_per_serving: float, servings_eaten: int = 1, db: AsyncSession = None) -> dict:
    if not db:
        raise ValueError("Database session is required")
    
    total = sodium_mg_per_serving * servings_eaten
    date_key = f"sodium_log_{datetime.utcnow().strftime('%Y-%m-%d')}"
    
    result = await db.execute(select(PalateProfile).where(PalateProfile.user_id == user_id))
    profile = result.scalars().first()
    
    if not profile:
        # If no profile exists, we can't log (or we'd create one, but let's assume it exists for active users)
        return {"error": "Palate profile not found"}
        
    current = profile.dish_context_weights or {}
    daily_log = current.get(date_key, {"total_mg": 0.0, "entries": []})
    daily_log["total_mg"] += total
    daily_log["entries"].append({
        "recommendation_id": recommendation_id,
        "sodium_mg": total,
        "timestamp": datetime.utcnow().isoformat()
    })
    current[date_key] = daily_log
    
    # Re-assign to trigger SQLAlchemy JSONB update
    profile.dish_context_weights = current
    
    # Must use flag_modified for JSONB if just mutating dict in place
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(profile, "dish_context_weights")
    
    await db.commit()
    return {"total_mg": daily_log["total_mg"]}

async def get_daily_sodium(user_id: str, date: str = None, db: AsyncSession = None) -> dict:
    if not db:
        raise ValueError("Database session is required")
        
    if not date:
        date = datetime.utcnow().strftime('%Y-%m-%d')
        
    limit = await get_user_sodium_limit(user_id, db)
    
    result = await db.execute(select(PalateProfile).where(PalateProfile.user_id == user_id))
    profile = result.scalars().first()
    
    if not profile or not profile.dish_context_weights:
        daily_log = {"total_mg": 0.0, "entries": []}
    else:
        date_key = f"sodium_log_{date}"
        daily_log = profile.dish_context_weights.get(date_key, {"total_mg": 0.0, "entries": []})
        
    return {
        "user_id": user_id,
        "date": date,
        "total_sodium_mg": daily_log["total_mg"],
        "entries": daily_log["entries"],
        "sodium_limit_mg": limit,
        "remaining_mg": max(0, limit - daily_log["total_mg"]),
        "percent_used": round(daily_log["total_mg"] / limit * 100, 1) if limit else 0.0,
        "within_limit": daily_log["total_mg"] <= limit
    }

async def get_weekly_sodium_summary(user_id: str, db: AsyncSession) -> dict:
    today = datetime.utcnow().date()
    days_data = []
    
    for i in range(7):
        target_date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        daily_stats = await get_daily_sodium(user_id, target_date, db)
        days_data.append({
            "date": target_date,
            "total_mg": daily_stats["total_sodium_mg"],
            "within_limit": daily_stats["within_limit"]
        })
        
    days_data.reverse() # Chronological order
    
    total_week_mg = sum(d["total_mg"] for d in days_data)
    average_daily_mg = total_week_mg / 7
    days_within_limit = sum(1 for d in days_data if d["within_limit"])
    days_over_limit = 7 - days_within_limit
    
    return {
        "user_id": user_id,
        "days": days_data,
        "average_daily_mg": round(average_daily_mg, 1),
        "days_within_limit": days_within_limit,
        "days_over_limit": days_over_limit
    }
