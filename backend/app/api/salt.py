from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.salt_type import SaltType
from typing import Any

router = APIRouter()

@router.get("-types", status_code=200)
async def get_salt_types(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    result = await db.execute(select(SaltType))
    salts = result.scalars().all()
    return [{"id": s.id, "name": s.name, "density_g_per_ml": s.density_g_per_ml, "sodium_mg_per_gram": s.sodium_mg_per_gram, "notes": s.notes} for s in salts]

@router.post("/convert")
async def convert_salt():
    return {"status": "not_implemented", "endpoint": "POST /salt/convert"}
