import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy import or_, and_, func
from app.db.models import User, Address, Relationship
from typing import Tuple, List

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _clean_string(self, value: str) -> str:
        return re.sub(r'\D', '', value) if value else ""

    async def get_by_id(self, user_id: int) -> User:
        stmt = select(User).options(selectinload(User.endereco)).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_relatives(self, user_id: int) -> List[Tuple[User, str, bool]]:
        # parentescos stores one row per pair; read both directions.
        # Returns (relative, grau as stored, reverse) - reverse=True when user_id is the related side.
        stmt = select(User, Relationship.grau, Relationship.related_user_id == user_id).join(
            Relationship,
            or_(
                and_(Relationship.user_id == user_id, Relationship.related_user_id == User.id),
                and_(Relationship.related_user_id == user_id, Relationship.user_id == User.id),
            ),
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def search(self, skip: int, limit: int, **kwargs) -> Tuple[List[User], int]:
        stmt = select(User).options(selectinload(User.endereco))
        conditions = []

        if kwargs.get('nome'):
            conditions.append(User.nome.ilike(f"%{kwargs['nome']}%"))
        if kwargs.get('cpf'):
            conditions.append(User.cpf == self._clean_string(kwargs['cpf']))
        if kwargs.get('telefone'):
            conditions.append(User.telefone.ilike(f"%{self._clean_string(kwargs['telefone'])}%"))
        if kwargs.get('data_nascimento'):
            conditions.append(User.data_nascimento == kwargs['data_nascimento'])
        if kwargs.get('endereco'):
            stmt = stmt.join(Address)
            conditions.append(
                or_(
                    Address.logradouro.ilike(f"%{kwargs['endereco']}%"),
                    Address.bairro.ilike(f"%{kwargs['endereco']}%")
                )
            )
        if kwargs.get('parente'):
            parente = aliased(User)
            stmt = stmt.join(Relationship, or_(User.id == Relationship.user_id, User.id == Relationship.related_user_id)).join(
                parente,
                or_(
                    and_(Relationship.user_id == User.id, Relationship.related_user_id == parente.id),
                    and_(Relationship.related_user_id == User.id, Relationship.user_id == parente.id),
                ),
            ).distinct()
            conditions.append(parente.nome.ilike(f"%{kwargs['parente']}%"))

        if kwargs.get('q'):
            term = f"%{kwargs['q']}%"
            generic_cond = or_(
                User.nome.ilike(term),
                User.cpf.ilike(term),
                User.telefone.ilike(term)
            )
            conditions.append(generic_cond)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all(), total

    async def get_neighbors(self, logradouro: str, bairro: str, numero: int, raio: int, current_user_id: int):
        stmt = select(User, Address).join(Address).where(
            and_(
                Address.logradouro == logradouro,
                Address.bairro == bairro,
                func.abs(Address.numero - numero) <= raio,
                User.id != current_user_id
            )
        )
        result = await self.db.execute(stmt)
        return result.all()
