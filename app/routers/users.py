from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Union
from app.db.database import get_db
from app.schemas.base import APIResponse, PaginatedData
from app.schemas.user import UserResponse, UserSummary
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.core.security import get_current_user, require_role
from app.db.models import RoleEnum
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/v1", tags=["Users"])

def get_user_service(db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    return UserService(repo)

@router.get("/usuarios/{user_id}", response_model=APIResponse[UserResponse])
@limiter.limit("30/minute")
async def get_user(
    request: Request,
    user_id: int, 
    service: UserService = Depends(get_user_service),
    current_user = Depends(require_role([RoleEnum.admin, RoleEnum.operator, RoleEnum.readonly]))
):
    logger.info(f"AUDIT: User {current_user.username} accessed /usuarios/{user_id}")
    user = await service.get_user_details(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return APIResponse(success=True, data=user)

@router.get("/busca", response_model=APIResponse[PaginatedData[Union[UserResponse, UserSummary]]])
@limiter.limit("20/minute")
async def generic_search(
    request: Request,
    q: Optional[str] = None,
    nome: Optional[str] = None,
    cpf: Optional[str] = None,
    telefone: Optional[str] = None,
    endereco: Optional[str] = None,
    parente: Optional[str] = None,
    completo: bool = Query(False, description="true = retorna dados completos (endereço, parentes, vizinhos) de cada resultado"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: UserService = Depends(get_user_service),
    current_user = Depends(require_role([RoleEnum.admin, RoleEnum.operator, RoleEnum.readonly]))
):
    logger.info(f"AUDIT: User {current_user.username} performed search. Filters provided.")
    paginated = await service.search_users(
        page=page, limit=limit, completo=completo, q=q, nome=nome, cpf=cpf, telefone=telefone, endereco=endereco, parente=parente
    )
    return APIResponse(success=True, data=paginated)
