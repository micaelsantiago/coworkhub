# Coworkhub

Fundação técnica do monólito Django descrito em [`docs/`](docs/README.md). Nesta etapa, o
repositório contém apenas o ambiente local, a autenticação global mínima e os esqueletos dos
módulos; regras de negócio ainda não foram implementadas.

## Pré-requisitos

- Docker Engine com Docker Compose
- `make` (opcional; todos os comandos podem ser executados diretamente com `docker compose`)

## Início rápido

```bash
make setup
make up
```

Acesse:

- Aplicação: <http://localhost:8000>
- Liveness: <http://localhost:8000/healthz>
- Readiness (PostgreSQL + Redis): <http://localhost:8000/readyz>
- Admin: <http://localhost:8000/admin/>

O serviço `web` aplica as migrações automaticamente no ambiente local. Para criar um usuário de
suporte:

```bash
docker compose exec web python manage.py createsuperuser
```

## Serviços locais

| Serviço | Responsabilidade |
|---|---|
| `web` | Django com servidor de desenvolvimento |
| `postgres` | PostgreSQL 16 |
| `redis` | Cache e broker |
| `worker` | Celery worker |
| `beat` | Agendador Celery |
| `frontend` | Watch de Tailwind CSS e bundle de HTMX/Alpine.js |

PostgreSQL e Redis têm portas publicadas apenas para facilitar ferramentas locais. Os serviços de
produção deverão usar somente a rede interna, conforme `docs/infraestrutura.md`.
Se as portas padrão já estiverem ocupadas, altere `POSTGRES_EXPOSED_PORT` e
`REDIS_EXPOSED_PORT` no `.env`. Em Linux, ajuste também `LOCAL_UID`/`LOCAL_GID` caso seu usuário
não utilize `1000:1000`.

## Comandos úteis

```bash
make test             # suíte pytest
make lint             # Ruff
make format           # formatação e correções seguras
make makemigrations   # gerar migrações
make migrate          # aplicar migrações
make shell            # shell do Django
make down             # encerrar os contêineres
```

As configurações estão separadas em `config/settings/base.py`, `dev.py`, `test.py` e `prod.py`.
Copie novas variáveis para `.env.example`, sem versionar segredos no `.env`.
