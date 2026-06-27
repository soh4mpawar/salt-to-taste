from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.schemas.recipe import RecipeCreate, RecipeImageUploadResponse
from app.schemas.recommendation import RecommendationRead
from app.utils.image_processing import validate_image_format
from app.services.recipe_service import process_recipe
from app.models.user import User

router = APIRouter()

@router.post("", response_model=RecommendationRead, status_code=201)
async def create_recipe(recipe_in: RecipeCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).limit(1))
    user = result.scalars().first()
    if not user:
        user = User(email="test@example.com", display_name="Test User")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return await process_recipe(
        raw_input=recipe_in.raw_content,
        input_type=recipe_in.source_type.value,
        user_id=user.id,
        db=db
    )

@router.post("/image-upload", response_model=RecipeImageUploadResponse, status_code=201)
async def upload_recipe_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    image_bytes = await file.read()
    
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        
    valid, reason = validate_image_format(image_bytes, file.filename)
    if not valid:
        raise HTTPException(status_code=415, detail=f"Unsupported format: {reason}")
        
    # Make sure user exists since FK is enforced
    user_uuid = UUID(user_id) if "-" in user_id else UUID("00000000-0000-0000-0000-000000000001")
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalars().first()
    if not user:
        user = User(id=user_uuid, email="test_upload@example.com", display_name="Test Upload")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return await process_recipe(
        raw_input=file.filename,
        input_type="image",
        user_id=user.id,
        db=db,
        image_bytes=image_bytes
    )

@router.get("/{recipe_id}")
async def get_recipe(recipe_id: UUID):
    return {"status": "not_implemented", "endpoint": "GET /recipes/{recipe_id}"}

@router.get("")
async def list_recipes():
    return {"status": "not_implemented", "endpoint": "GET /recipes"}
