from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import get_db
from app.schemas.base import APIResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=APIResponse)
async def health_check():
    return APIResponse(success=True, message="API is running OK")

@router.get("/health/db", response_model=APIResponse)
async def db_health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return APIResponse(success=True, message="Database is connected")
    except Exception as e:
        return APIResponse(success=False, message="Database connection failed", error_code="DB_FAIL")
