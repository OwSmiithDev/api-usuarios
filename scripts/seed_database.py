import asyncio
import argparse
import random
from faker import Faker
from sqlalchemy import select
from app.db.database import AsyncSessionLocal, engine
from app.db.models import User, Address, Relationship, ApiUser, RoleEnum
from app.core.security import get_password_hash

fake = Faker('pt_BR')

def fake_cpf():
    return f"{random.randint(100,999)}{random.randint(100,999)}{random.randint(100,999)}{random.randint(10,99)}"

async def seed_data(count: int):
    async with AsyncSessionLocal() as session:
        if not await session.scalar(select(ApiUser).where(ApiUser.username == "admin")):
            session.add(ApiUser(username="admin", hashed_password=get_password_hash("admin123"), role=RoleEnum.admin))
        
        users_list = []
        ruas_ficticias = [fake.street_name() for _ in range(max(1, count // 10))]
        bairros_ficticios = [fake.neighborhood() for _ in range(max(1, count // 20))]

        for _ in range(count):
            user = User(
                nome=fake.name(),
                data_nascimento=fake.date_of_birth(minimum_age=18, maximum_age=90),
                cpf=fake_cpf(),
                telefone=fake.msisdn()[:11]
            )
            end = Address(
                logradouro=random.choice(ruas_ficticias),
                numero=random.randint(1, 100),
                bairro=random.choice(bairros_ficticios),
                cidade=fake.city(),
                estado=fake.state_abbr(),
                cep=fake.postcode()
            )
            user.endereco = end
            users_list.append(user)
            session.add(user)
        
        await session.commit()
        
        for _ in range(count // 5):
            u1, u2 = random.sample(users_list, 2)
            if u1.id and u2.id:
                rel = Relationship(user_id=u1.id, related_user_id=u2.id, grau=random.choice(["Irmão(ã)", "Primo(a)", "Pai/Mãe"]))
                session.add(rel)
        
        try:
            await session.commit()
            print(f"✅ {count} usuários e relacionamentos gerados com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar relacionamentos: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Popula o banco com dados fictícios")
    parser.add_argument("--count", type=int, default=500, help="Quantidade de usuários")
    args = parser.parse_args()
    asyncio.run(seed_data(args.count))
