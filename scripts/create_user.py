"""Cria (ou atualiza a senha de) um usuário da API.

Uso:
    docker compose exec api python scripts/create_user.py --username teste --password 'SENHA' --role readonly

Roles: admin | operator | readonly
"""
import argparse
import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import ApiUser, RoleEnum
from app.core.security import get_password_hash


async def upsert_user(username: str, password: str, role: str) -> None:
    role_enum = RoleEnum(role)  # ValueError se inválido
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(ApiUser).where(ApiUser.username == username))
        if existing:
            existing.hashed_password = get_password_hash(password)
            existing.role = role_enum
            action = "atualizado"
        else:
            session.add(ApiUser(username=username, hashed_password=get_password_hash(password), role=role_enum))
            action = "criado"
        await session.commit()
    print(f"Usuário '{username}' {action} com role '{role}'.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Cria ou atualiza um usuário da API")
    p.add_argument("--username", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--role", default="readonly", choices=[r.value for r in RoleEnum])
    args = p.parse_args()
    asyncio.run(upsert_user(args.username, args.password, args.role))
