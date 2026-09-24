from app.repositories.user_repository import UserRepository
from app.core.config import settings
from app.schemas.user import UserResponse, UserSummary, RelativeSchema, NeighborSchema, AddressSchema
from app.schemas.base import PaginatedData
import math

# grau describes the related user as seen by user_id ("related is Pai/Mãe of user_id"); flip it for the other side.
# Symmetric degrees (Irmão(ã), Primo(a)) are not listed and stay as-is.
GRAU_INVERSO = {"Pai/Mãe": "Filho(a)", "Filho(a)": "Pai/Mãe"}

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user_details(self, user_id: int) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            return None

        vizinhos_data = []
        if user.endereco:
            neighbors_raw = await self.repo.get_neighbors(
                user.endereco.logradouro,
                user.endereco.bairro,
                user.endereco.numero,
                settings.RAIO_VIZINHANCA,
                user.id
            )
            for u, _ in neighbors_raw:
                vizinhos_data.append(NeighborSchema(nome=u.nome, cpf=u.cpf))

        parentes_data = [
            RelativeSchema(nome=p.nome, cpf=p.cpf, grau=GRAU_INVERSO.get(grau, grau) if reverse else grau)
            for p, grau, reverse in await self.repo.get_relatives(user.id)
        ]

        return UserResponse(
            id=user.id,
            nome=user.nome,
            data_nascimento=user.data_nascimento,
            cpf=user.cpf,
            telefone=user.telefone,
            endereco=AddressSchema.model_validate(user.endereco) if user.endereco else None,
            parentes=parentes_data,
            vizinhos=vizinhos_data,
        )

    async def search_users(self, page: int, limit: int, completo: bool = False, **kwargs) -> PaginatedData:
        skip = (page - 1) * limit
        users, total = await self.repo.search(skip, limit, **kwargs)
        pages = math.ceil(total / limit) if limit else 0
        if completo:
            # ponytail: 2-3 queries per user (details + neighbors), fine for limit<=100; batch-load if it gets slow
            items = [await self.get_user_details(u.id) for u in users]
        else:
            items = [UserSummary.model_validate(u) for u in users]
        return PaginatedData(items=items, total=total, page=page, limit=limit, pages=pages)