import os
import sys
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "contract.db")
os.environ["SESSION_SECRET"] = "test-only-secret-not-for-prod"
os.environ["APP_ENV"] = "dev"
os.environ["CORS_ORIGINS"] = "*"

from sqlalchemy import BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles

@compiles(JSONB, "sqlite")
def _jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):
    return "INTEGER"

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.main import app

EMAIL = "tester@lifemaps.pro"
PASSWORD = "SenhaForte123"
NEW_PASSWORD = "NovaSenha456"

results = []

def check(name, cond, extra=""):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (f" | {extra}" if extra else ""))

with TestClient(app, base_url="https://testserver") as c:
    r = c.get("/api/health")
    check("health 200", r.status_code == 200 and r.json()["status"] == "ok", r.status_code)

    r = c.post("/api/auth/register", json={"email": EMAIL, "password": PASSWORD, "name": "Tester"})
    check("register 200", r.status_code == 200 and r.json()["email"] == EMAIL, r.status_code)

    r = c.post("/api/auth/register", json={"email": EMAIL, "password": PASSWORD})
    check("register duplicado 409", r.status_code == 409, r.status_code)

    r = c.get("/api/auth/me")
    check("me logado", r.status_code == 200 and r.json()["email"] == EMAIL, r.status_code)

    r = c.post("/api/auth/logout")
    check("logout 204", r.status_code == 204, r.status_code)

    r = c.get("/api/auth/me")
    check("me sem sessao 401", r.status_code == 401, r.status_code)

    r = c.post("/api/auth/login", json={"email": EMAIL, "password": "errada000"})
    check("login senha errada 401", r.status_code == 401, r.status_code)

    r = c.post("/api/auth/login", json={"email": EMAIL, "password": PASSWORD})
    check("login ok 200", r.status_code == 200 and r.json()["email"] == EMAIL, r.status_code)

    r = c.post("/api/auth/refresh")
    check("refresh 200", r.status_code == 200 and r.json()["email"] == EMAIL, r.status_code)

    r = c.post("/api/docs")
    check("docs create 201", r.status_code == 201, r.status_code)
    doc_id = r.json()["id"]

    r = c.put(f"/api/docs/{doc_id}", json={"data": {"n1": ["ok"]}, "base_version": 1})
    check("docs put v2", r.status_code == 200 and r.json()["version"] == 2, r.status_code)

    r = c.put(f"/api/docs/{doc_id}", json={"data": {"x": 1}, "base_version": 1})
    check("docs put 409 stale", r.status_code == 409, r.status_code)

    r = c.get("/api/docs")
    check("docs list 1", r.status_code == 200 and len(r.json()) == 1, r.status_code)

    r = c.post("/api/auth/forgot-password", json={"email": EMAIL})
    body = r.json()
    check("forgot 200 + dev_token", r.status_code == 200 and body.get("status") is True and body.get("dev_token"), r.status_code)
    reset_token = body.get("dev_token", "")

    r = c.post("/api/auth/forgot-password", json={"email": "nao_existe@x.com"})
    check("forgot email inexistente generico", r.status_code == 200 and r.json()["status"] is True and "dev_token" not in r.json(), r.status_code)

    r = c.post("/api/auth/reset-password", json={"email": EMAIL, "token": "token-invalido", "password": NEW_PASSWORD})
    check("reset token invalido 400", r.status_code == 400, r.status_code)

    r = c.post("/api/auth/reset-password", json={"email": EMAIL, "token": reset_token, "password": NEW_PASSWORD})
    check("reset ok 200", r.status_code == 200 and r.json()["email"] == EMAIL, r.status_code)

    r = c.post("/api/auth/logout")
    check("logout apos reset 204", r.status_code == 204, r.status_code)

    r = c.get("/api/auth/me")
    check("me sem sessao pos-reset 401", r.status_code == 401, r.status_code)

    r = c.post("/api/auth/login", json={"email": EMAIL, "password": PASSWORD})
    check("senha antiga invalida 401", r.status_code == 401, r.status_code)

    r = c.post("/api/auth/login", json={"email": EMAIL, "password": NEW_PASSWORD})
    check("login senha nova 200", r.status_code == 200, r.status_code)

failed = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(failed)}/{len(results)} PASS")
if failed:
    print("FAILED:", failed)
    sys.exit(1)