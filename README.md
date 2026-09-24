# API de Usuários (FastAPI + PostgreSQL)

API REST completa focada em performance e escalabilidade, feita para buscar e consultar relacionamentos e vizinhanças.

## Arquitetura
* **Backend:** Python 3.11 + FastAPI
* **ORM & Migrations:** SQLAlchemy 2 (Async) + Alembic
* **Database:** PostgreSQL (via `asyncpg`)
* **Autenticação:** JWT Token + RBAC (Roles: Admin, Operator, Readonly)
* **Segurança:** Rate Limit em memória (`slowapi`), Proteção contra SQL Injection (uso estrito de ORM).

## Como Rodar Localmente (Docker - Recomendado)

1. Crie o arquivo `.env`:
   ```bash
   cp .env.example .env
   ```
2. Suba a infraestrutura:
   ```bash
   docker compose up -d --build
   ```
3. Gere os dados fictícios:
   ```bash
   docker compose exec api python scripts/seed_database.py --count 500
   ```
4. Acesse a documentação Swagger: `http://localhost:8080/docs`
