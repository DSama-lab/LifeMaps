# Life Maps — Deploy na VPS (runbook p/ executar SEM o opencode)

> Guia auto-contido para subir o backend SaaS (Fase 2B) no VPS **sem precisar do opencode**.
> Stack: Docker Compose (postgres + api + caddy) sobre aaPanel/Portainer.
> Domínio sugerido: `api.lifemaps.pro` (ajuste onde aparecer).

---

## 1. Pré-requisitos (na VPS)

- Docker + Docker Compose v2 instalados.
  - aaPanel já traz Docker; se o comando `docker compose version` falhar, no painel: **App Store → Docker Manager → instalar**.
- Domínio apontado p/ o IP da VPS (regra de DNS **A**, no dashboard da Hostinger):
  - `api.lifemaps.pro` → `148.230.78.83` (ou IP real da VPS).
- Portas **80 e 443 livres** (ver conflito na seção 6).
- Acesso SSH à VPS (ou terminal do Portainer).

## 2. Pegar o código

```bash
cd /root
git clone https://github.com/DSama-lab/LifeMaps.git
cd LifeMaps/backend
```

(Se já tinha clone: `cd LifeMaps && git pull`.)

## 3. Criar o `.env` (guardar credenciais aqui — NUNCA em MDs/repo)

```bash
cp .env.example .env
nano .env
```

Preencher no `.env`:
| Variável | Valor |
|---|---|
| `POSTGRES_USER` | `postgres` (ou outro) |
| `POSTGRES_PASSWORD` | **senha forte sua** (ex.: `openssl rand -base64 24`) |
| `POSTGRES_DB` | `lifemaps` |
| `DATABASE_URL` | `postgresql+psycopg://postgres:<MESMA SENHA>@postgres:5432/lifemaps` |
| `SESSION_SECRET` | gere: `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `GOOGLE_CLIENT_ID` | (opcional p/ login Google — veja seção 8) |
| `GOOGLE_CLIENT_SECRET` | (opcional — colocado SÓ no servidor) |
| `CORS_ORIGINS` | origens que vão chamar a API. Ex.: `https://app.lifemaps.pro` (front que escolher usar). Sem barra final. |
| `DOMAIN` | `api.lifemaps.pro` (essa variável o Caddy lê p/ o TLS) |
| `DOC_MAX_BYTES` | `5242880` (padrão) |
| `RATE_LOGIN_PER_MIN` | `10` (padrão) |
| `RATE_DOC_PUT_PER_MIN` | `60` (padrão) |

## 4. Subir

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Acompanhar:
```bash
docker compose -f docker-compose.prod.yml logs -f api
```

Ver o Caddy emitir o certificado (primeira vez demora ~10-30s):
```bash
docker compose -f docker-compose.prod.yml logs -f caddy
```

## 5. Testar

```bash
curl https://api.lifemaps.pro/api/health
# esperado: {"status":"ok"}
curl -i https://api.lifemaps.pro/api/auth/me
# 401 (não autenticado) = normal; HTTPS + CORS funcionando
```

Docs interativas (dá pra testar login na hora): `https://api.lifemaps.pro/docs`

## 6. CONFLITO de porta 80/443 (importante no aaPanel)

aaPanel/Traefik/Nginx normalmente **já ocupam 80/443**. Se o `caddy` não subir ou o Nginx "roubar" a porta, use o caminho alternativo:

1. Editar `docker-compose.prod.yml`: **remover o serviço `caddy`** e descomentar em `api`:
   ```yaml
   ports:
     - "127.0.0.1:8000:8000"
   ```
2. `docker compose -f docker-compose.prod.yml up -d --build` (só postgres + api).
3. No aaPanel: criar site `api.lifemaps.pro` (Nginx + SSL Let's Encrypt).
4. Nginx → Configuração → no bloco `location /`, trocar por:
   ```nginx
   location / {
       proxy_pass http://127.0.0.1:8000;
       proxy_set_header Host $host;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_read_timeout 300s;
   }
   ```
5. Salvar. O `api:8000` vira `127.0.0.1:8000` — mesmo contrato.

## 7. Front (o app do usuário)

O `SYNC_API_BASE` do app já decide sozinho: se a página for aberta em `localhost` usa `http://127.0.0.1:8000`; senão usa `https://api.lifemaps.pro`. Ou seja, **subir o `index.html` num domínio HTTPS é suficiente** — o ☁️ aponta pro backend certo sem configurar nada.

- Serve o front com aaPanel (site estático) ou pelo próprio Caddy (bloco comentado no `Caddyfile.prod`) ou GitHub Pages.
- Qualquer domínio usado como front deve entrar em `CORS_ORIGINS` no `.env` (reiniciar a api: `docker compose restart api`).
- Para mudar o host da API manualmente (útil em teste): o dono abre o console do navegador e roda `localStorage.setItem('mv_api_base','https://api.lifemaps.pro')` e recarrega.

### 7.1 Deploy do front via aaPanel (file manager) — passo a passo

**Pré-requisito**: ter o `index.html` atualizado localmente (rodar `node build-demo.js` após cada edição do app).

1. Ler o arquivo local: `LIFEMAPS  PROJECT/index.html` (o app demo, sem credenciais).
2. Abrir o aaPanel: `https://148.230.78.83:24186` → entrar com as credenciais de login (digitadas na hora).
3. Menu lateral **Arquivos** → navegar ao site do LifeMaps. O `index.html` fica no docroot do vhost `lifemaps.blackops7.pro` (caminho típico: `/www/wwwroot/lifemaps.blackops7.pro/index.html`).
4. **Antes de substituir**: criar uma cópia de segurança de segurança do atual:
   - Clique direito no `index.html` → **Renomear** → `index.html.bak` (ou usar a ferramenta de cópia do painel).
5. Com o painel na pasta do site:
   - Clicar **Upload** (botão no topo da lista de arquivos, módulo "Upload de Arquivo").
   - **Enviar Arquivo** (campo de seleção que abre o file chooser) → escolher o `index.html` local.
   - Autorizar o envio quando o navegador pedir.
   - **Confirmar Upload**.
   - Aparece o diálogo de conflito → escolher **Sobrescrever** (não "renomear"/"pular").
6. Confirmar que o arquivo novo está no ar: abrir `https://lifemaps.blackops7.pro/index.html?cv=0917` → deve aparecer o gate/login e, após logar, o app com drawer ☰ + busca no topo + chips.
7. Limpeza (se quiser): remover `index.html.bak` só depois de validar que o novo está OK.
8. Testar no navegador: login (email+senha e Google), painel, mapa, sync ☁️. Console do navegador deve mostrar só o 401 esperado do probe `/api/auth/me` (se o backend ainda não subiu, é `ERR_CONNECTION_REFUSED` — console limpo no restante).

> **Importante (lição de incidente)**: na API/Ferramentas do aaPanel, o `path` **sempre** deve ser o caminho completo do **arquivo** (`/www/wwwroot/lifemaps.blackops7.pro/index.html`), NUNCA o diretório — deletar com `path` de diretório move a pasta inteira para a Lixeira (site 404).

## 8. Login Google (opcional — ativa só quando configurado)

1. `console.cloud.google.com` → API & Services → Credentials → **OAuth 2.0 Client ID (Web)**.
   - Authorized redirect URIs **não se aplicam** ao fluxo usado (id_token direto), mas coloque `https://api.lifemaps.pro` na lista de origins.
2. `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` no `.env` do backend. Reiniciar a api.
3. **Botão Google no front**: para ele aparecer, o front precisa saber o client_id. Duas opções:
   - Servir o site com a variável pública `LIFEMAPS_GOOGLE_CLIENT_ID` setada no ambiente de deploy, **ou**
   - No browser do dono: `localStorage.setItem('mv_google_client_id','SEU_CLIENT_ID_PUBLICO')` + reload.
   - (E-mail+senha já funciona SEM essa configuração.)

## 9. Backup agendado (obrigatório)

```bash
crontab -e
```
Acrescentar (roda 03:00 UTC diário):
```cron
0 3 * * * cd /root/LifeMaps/backend && docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U postgres lifemaps > /root/backups/lifemaps_$(date +\%F).sql && find /root/backups -name '*.sql' -mtime +30 -delete
```
Criar a pasta antes: `mkdir -p /root/backups`. **Testar a restauração** pelo menos 1×/mês:
```bash
docker compose -f docker-compose.prod.yml exec -T postgres psql -U postgres -c "DROP DATABASE IF EXISTS lifemaps_restore;" && docker compose -f docker-compose.prod.yml exec -T postgres createdb -U postgres lifemaps_restore && docker compose -f docker-compose.prod.yml exec -T postgres sh -c "gunzip -c - > /dev/null" < /root/backups/lifemaps_YYYY-MM-DD.sql
```

## 10. Segurança — checklist

- [ ] Porta 5432 do postgres **sem mapeamento** público (o compose já garante).
- [ ] Firewall do aaPanel: liberar só 80/443 (e 22 p/ SSH).
- [ ] `SESSION_SECRET` único + longo.
- [ ] `CORS_ORIGINS` restrito aos domínios reais.
- [ ] Credenciais SÓ no `.env` (gitignore). Nenhum MD/repo com valor real.

## Solução de problemas

| Sintoma | Provável | Ação |
|---|---|---|
| `curl http://.../api/health` ok mas `https://` não responde | Caddy sem certificado / DNS ainda propagando | `logs -f caddy`; ver se o domínio resolve no VPS: `dig api.lifemaps.pro` |
| API responde 500 no boot | `DATABASE_URL` com senha errada | comparar senha do `DATABASE_URL` e `POSTGRES_PASSWORD`; ver `logs api` |
| 409 ao salvar do app | doc foi alterado em outro device | é o comportamento correto (pull automático) |
| 401 no login Google | client_id/secret errados | checar `.env`; ver `logs api` |
| CORS blocked no console do browser | front fora do `CORS_ORIGINS` | adicionar domínio, `docker compose restart api` |