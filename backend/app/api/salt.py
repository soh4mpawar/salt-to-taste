from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.salt_type import SaltType
from typing import Any
from app.schemas.salt_converter import SaltConversionRequest, SaltConversionResponse
from app.services.salt_service import convert_salt, get_all_conversion_ratios

router = APIRouter()

@router.get("-types", status_code=200)
async def get_salt_types(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    result = await db.execute(select(SaltType))
    salts = result.scalars().all()
    return [{"id": s.id, "name": s.name, "density_g_per_ml": s.density_g_per_ml, "sodium_mg_per_gram": s.sodium_mg_per_gram, "notes": s.notes} for s in salts]

@router.post("/convert", response_model=SaltConversionResponse)
async def convert_salt_type(
    request: SaltConversionRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = convert_salt(
            from_name=request.from_salt_name,
            to_name=request.to_salt_name,
            amount_grams=request.amount_grams
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/convert-all")
async def convert_to_all_salts(
    from_salt_name: str,
    amount_grams: float,
    db: AsyncSession = Depends(get_db)
):
    try:
        results = get_all_conversion_ratios(from_salt_name, amount_grams)
        return {"conversions": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
