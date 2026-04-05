# Gestor de Despensa API

Backend em FastAPI para o projeto Gestor de Despensa.

## Stack

- FastAPI
- SQLAlchemy 2
- Alembic
- PostgreSQL
- Railway

## Setup local

1. Copie `.env.example` para `.env`
2. Suba o PostgreSQL local com `docker compose up -d`
3. Instale dependências com `pip install -e .[dev]`
4. Rode migrações com `alembic upgrade head`
5. Inicie a API com `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## Railway

O projeto está pronto para usar `DATABASE_URL` injetada pelo PostgreSQL do Railway.
O backend normaliza automaticamente URLs `postgres://` e `postgresql://` para o driver
interno `postgresql+psycopg://`.

Para desenvolvimento local apontando para um banco hospedado no Railway, o backend tambem aceita
`DATABASE_PUBLIC_URL` como fallback. Isso evita usar hosts `*.railway.internal`, que so resolvem
dentro da rede privada do Railway.

Fluxo esperado:

1. Criar serviço da API
2. Adicionar banco PostgreSQL no projeto Railway
3. Garantir que `DATABASE_URL` foi conectada ao serviço
4. Subir a aplicação com o comando configurado em `railway.json`

Observação: no Railway, a expansão de `${PORT:-8000}` precisa rodar dentro de um shell.
Por isso o `startCommand` usa `sh -c ...`; se o comando for executado diretamente, o
`uvicorn` recebe a string literal `${PORT:-8000}` e falha ao iniciar.
