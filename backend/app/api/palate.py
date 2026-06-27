from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import os

from app.core.database import get_db
from app.services.palate_service import get_palate_summary
from app.agents.personalization_engine import PalateModelManager
from app.schemas.palate import PalateHistoryItem

router = APIRouter()

@router.get("/{user_id}", status_code=200)
async def get_user_palate(user_id: str, db: AsyncSession = Depends(get_db)):
    summary = await get_palate_summary(user_id, db)
    return summary

@router.delete("/{user_id}/reset", status_code=200)
async def reset_user_palate(user_id: str, db: AsyncSession = Depends(get_db)):
    manager = PalateModelManager(model_dir="models")
    model_path = manager.get_model_path(user_id)
    count_path = model_path + ".count"
    
    if os.path.exists(model_path):
        os.remove(model_path)
    if os.path.exists(count_path):
        os.remove(count_path)
        
    await db.execute(
        text("""
        UPDATE palate_profiles 
        SET weights_json = '{}', dish_context_weights = '{}', total_feedback_count = 0 
        WHERE user_id = :user_id
        """),
        {"user_id": user_id}
    )
    await db.commit()
    
    return {"status": "reset", "user_id": user_id}

@router.get("/{user_id}/history", response_model=list[PalateHistoryItem], status_code=200)
async def get_palate_history(user_id: str, db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT uf.rating, uf.notes, uf.created_at,
               rsr.baseline_grams, rsr.personalized_grams,
               rsr.recommendation_context
        FROM user_feedback uf
        JOIN recipe_salt_recommendations rsr ON uf.recommendation_id = rsr.id
        WHERE rsr.user_id = :user_id
        ORDER BY uf.created_at DESC
        LIMIT 20
    """)
    result = await db.execute(query, {"user_id": user_id})
    rows = result.mappings().fetchall()
    return rows
