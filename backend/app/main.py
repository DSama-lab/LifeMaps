import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import config
from .db import init_db
from .routers import auth, docs

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Life Maps API",
    version="0.1.0",
    description=(
        "Backend SaaS do Life Maps: armazena o documento JSON do plano de mobilidade "
        "por usuário. Autenticação por Google OAuth ou senha (sessão httpOnly)."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(docs.router)


@app.on_event("startup")
def on_startup():
    if config.DATABASE_URL and config.SESSION_SECRET:
        init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def unhandled(request, exc):
    logging.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"detail": "Erro interno"})