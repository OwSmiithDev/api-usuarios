from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.db.database import get_db
from app.db.models import ApiUser
from app.core.security import verify_password, create_access_token
from app.schemas.auth import Token

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # brute-force protection on credentials
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApiUser).where(ApiUser.username == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}
