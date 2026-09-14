# Life Maps Backend — API SaaS

Backend do Life Maps (Fase 2A do [`PLANO-SAAS-SEGURANCA.md`](../../MDs%20Projects/Lifemaps/PLANO-SAAS-SEGURANCA.md)).

Stack: **FastAPI + SQLAlchemy + Postgres (JSONB) + Google OAuth/senha, sessão em cookie httpOnly**.
Sem Supabase — Postgres próprio no Docker do aaPanel do dono. Alternativa apletida em `docker-compose.yml`.

## Estrutura

```
backend/
  app/
    main.py        # FastAPI + CORS + routers
    config.py      # lê .env (anti-credencial: só .env.example versionado)
    db.py          # engine/sessão SQLAlchemy + init_db (create_all)
    models.py      # users + docs (User, Document; data = JSONB)
    schemas.py     # Pydantic (validação de entrada/saída)
    security.py    # Argon2id, cookie de sessão, rate limit, auth dependency
    routers/
      auth.py      # /api/auth/google, /register, /login, /logout, /me
      docs.py      # GET/PUT/POST /api/docs — documento do plano do usuário
  Dockerfile
  docker-compose.yml   # postgres (no ports p/ fora) + api + caddy (80/443)
  Caddyfile            # TLS automático (Let's Encrypt) + headers de segurança
  .env.example         # cópie e preencha em .env (NUNCA versionar credenciais)
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/google` | Login com Google (`id_token`) — valida JWKS/issuer/audience no servidor |
| POST | `/api/auth/register` | Cadastro com senha (Argon2id) |
| POST | `/api/auth/login` | Login com senha |
| POST | `/api/auth/logout` | Encerra sessão |
| GET | `/api/auth/me` | Usuário da sessão atual |
| GET | `/api/docs/{id}` | Lê o documento (só do dono) |
| PUT | `/api/docs/{id}` | Grava o documento inteiro (JSON) — com atualização otimista (`base_version`) e limite de tamanho |
| POST | `/api/docs` | Cria um documento em branco |
| GET | `/api/health` | Healthcheck |

## Rodando (local)

**Requisito**: Python 3.12 ou 3.13 — `pydantic-core` não tem wheel pré-compilado para Python 3.14 no Windows (falta Visual C++ Build Tools para compilar; sem Docker local). Se tiver Python 3.12/3.13 instalado ou Docker Desktop, o `pip install -r requirements.txt` funciona normalmente.

1. `python -m venv .venv` e ative.
2. `pip install -r requirements.txt`
3. `copy .env.example .env` e preencha (Postgres local: `DATABASE_URL=postgresql+psycopg://postgres:SENHA@localhost:5432/lifemaps`; gere `SESSION_SECRET` com `python -c "import secrets; print(secrets.token_urlsafe(48))"`).
4. Crie o banco `lifemaps` no Postgres.
5. `uvicorn app.main:app --reload` → docs interativas em `http://127.0.0.1:8000/docs`.

## Rodando no VPS (aaPanel/Docker)

```bash
cp .env.example .env        # preencha TODAS as variáveis (DOMAIN incluso)
docker compose up -d --build
docker compose logs -f api
```

- Postgres: **sem porta pública** (só rede interna) — nunca mapeie 5432 no compose.
- Caddy expõe 80/443 com HTTPS automático; aponte o DNS antes.
- Backup: `docker compose exec postgres pg_dump -U postgres lifemaps > backup_$(date +%F).sql` agendado por cron + teste de restauração.

## Segurança (resumo)

- Senhas com **Argon2id**; sessão em **cookie `HttpOnly; Secure; SameSite=Lax`** (nada no localStorage).
- `id_token` do Google verificado no servidor (`google-auth` + JWKS).
- `PUT` valida propriedade do documento, tamanho (padrão 5 MiB) e concorrência (`base_version`).
- Rate limit em login/registro e em gravação (in-memory por IP; troque por Redis se multi-instância).
- CORS restrito aos domínios em `CORS_ORIGINS`.
- Segredos só em `.env` (gitignored). Nenhuma credencial real em arquivos ou MDs.

## Próximos passos

- Integrar `index.html` (trocar `localStorage` por `GET/PUT /api/docs` quando autenticado).
- Deploy no VPS + runbook + backup agendado (Fase 2B do plano).
- Tests automatizados (pytest + Postgres de teste).