"""Bootstrap idempotente para produção. Roda no start do container, depois do alembic.

- Cria/atualiza os usuários da API (admin + teste) a partir de variáveis de ambiente.
- Popula dados fictícios só se a tabela de usuários estiver vazia (não duplica a cada restart).

Env usados (todos opcionais):
  BOOTSTRAP_ADMIN_USER / BOOTSTRAP_ADMIN_PASSWORD
  BOOTSTRAP_TEST_USER  / BOOTSTRAP_TEST_PASSWORD
  BOOTSTRAP_SEED_COUNT  (default 100; 0 = não popular)
"""
import asyncio
import os
from sqlalchemy import select, func
from app.db.database import AsyncSessionLocal
from app.db.models import ApiUser, RoleEnum, User
from app.core.security import get_password_hash


async def _upsert(session, username: str, password: str, role: RoleEnum) -> None:
    existing = await session.scalar(select(ApiUser).where(ApiUser.username == username))
    if existing:
        existing.hashed_password = get_password_hash(password)
        existing.role = role
    else:
        session.add(ApiUser(username=username, hashed_password=get_password_hash(password), role=role))


async def main() -> None:
    admin_user = os.getenv("BOOTSTRAP_ADMIN_USER", "admin")
    admin_pw = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
    test_user = os.getenv("BOOTSTRAP_TEST_USER", "teste")
    test_pw = os.getenv("BOOTSTRAP_TEST_PASSWORD")
    seed_count = int(os.getenv("BOOTSTRAP_SEED_COUNT", "100"))

    async with AsyncSessionLocal() as session:
        if admin_pw:
            await _upsert(session, admin_user, admin_pw, RoleEnum.admin)
        if test_pw:
            await _upsert(session, test_user, test_pw, RoleEnum.readonly)
        await session.commit()

        total = await session.scalar(select(func.count()).select_from(User))
        print(f"bootstrap: usuarios existentes = {total}")

    if seed_count > 0 and (total or 0) == 0:
        from scripts.seed_database import seed_data
        await seed_data(seed_count)
    else:
        print("bootstrap: seed pulado (ja ha dados ou count=0)")


if __name__ == "__main__":
    asyncio.run(main())
