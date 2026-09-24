# API de Busca de Usuários (FastAPI + PostgreSQL)

API REST para cadastro e **busca de pessoas** com relacionamentos familiares e cálculo automático de vizinhança. Construída com foco em performance, segurança e boas práticas.

## Funcionalidades

- **Busca flexível** por nome, CPF, telefone, endereço ou parente — com paginação.
- **Modo `completo`**: em uma única chamada, retorna a pessoa com endereço, parentes (nome + CPF + grau) e vizinhos.
- **Parentesco nos dois sentidos**: se A é parente de B, B também aparece como parente de A (com o grau invertido: Pai/Mãe ↔ Filho(a)).
- **Vizinhança automática**: pessoas na mesma rua/bairro dentro de um raio configurável de números.
- **Autenticação JWT + RBAC**: papéis `admin`, `operator`, `readonly`.
- **Rate limiting** no login (5/min) e nas buscas — proteção contra força bruta e abuso.

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11 + FastAPI |
| ORM / Migrations | SQLAlchemy 2 (async) + Alembic |
| Banco | PostgreSQL (via `asyncpg`) |
| Auth | JWT (`python-jose`) + bcrypt (`passlib`) |
| Rate limit | `slowapi` |
| Container | Docker + Docker Compose |

## Arquitetura

Separação em camadas: **router → service → repository → model**. Os routers só tratam HTTP; a lógica de negócio fica nos services; o acesso ao banco fica isolado nos repositories. Toda query usa o ORM (sem SQL concatenado).

```
app/
  routers/       # endpoints HTTP (auth, users, health)
  services/      # regras de negócio (busca, vizinhança, parentesco)
  repositories/  # acesso ao banco (queries)
  schemas/       # contratos de entrada/saída (Pydantic)
  db/            # models e engine
  core/          # config, segurança (JWT), tratamento de erros
```

## Como rodar (Docker)

```bash
cp .env.example .env      # gere segredos fortes (comandos estão no arquivo)
docker compose up -d --build
docker compose exec api python scripts/seed_database.py --count 100
```

- Documentação interativa (Swagger): http://localhost:8080/docs
- OpenAPI (spec): http://localhost:8080/openapi.json

Crie um usuário:

```bash
docker compose exec api python scripts/create_user.py --username teste --password 'SUA_SENHA' --role readonly
```

## Exemplos de uso

```bash
# 1. Login → token
curl -X POST http://localhost:8080/api/v1/auth/login -d "username=admin&password=SUA_SENHA"

# 2. Busca simples
curl -H "Authorization: Bearer <TOKEN>" "http://localhost:8080/api/v1/busca?nome=silva"

# 3. Busca com dados completos (endereço, parentes, vizinhos)
curl -H "Authorization: Bearer <TOKEN>" "http://localhost:8080/api/v1/busca?telefone=5511999999999&completo=true"

# 4. Detalhe de uma pessoa
curl -H "Authorization: Bearer <TOKEN>" "http://localhost:8080/api/v1/usuarios/1"
```

### Filtros do `/api/v1/busca`

| Parâmetro | Busca por |
|---|---|
| `q` | nome, CPF ou telefone (genérico) |
| `nome`, `cpf`, `telefone` | campo específico |
| `endereco` | logradouro ou bairro |
| `parente` | nome de um parente |
| `completo` | `true` retorna os dados completos de cada resultado |
| `page`, `limit` | paginação (`limit` até 100) |

## Segurança

- Senhas com **bcrypt** (nunca em texto puro).
- **JWT** assinado; rotas protegidas por papel (RBAC).
- **Rate limiting** no login e nas buscas.
- **Sem SQL injection**: uso estrito do ORM, queries parametrizadas.
- Container roda como **usuário não-root**.
- Segredos ficam em variáveis de ambiente — nunca no código.

## Testes

```bash
docker compose exec api python -m pytest
```

## Melhorias futuras

- Testes de integração cobrindo busca, parentesco e vizinhança.
- Cache (Redis) para buscas frequentes.
- Endpoints de escrita (criar/editar pessoas) com validação e auditoria.
- Paginação por cursor para grandes volumes.

---

Dados de exemplo são gerados com **Faker** (pt_BR) — todos fictícios.
