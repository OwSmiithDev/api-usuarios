from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.routers import auth, users, health
from app.core.config import settings
from app.core.exceptions import global_exception_handler, custom_http_exception_handler
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = FastAPI(
    title="API de Pesquisa de Usuários",
    description="API RESTful para pesquisa, relacionamentos e cálculo automático de vizinhança",
    version="1.0.0"
)

_cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(',') if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    # Bearer-token API (no auth cookies); credentials must stay False, and the browser
    # rejects "*" combined with credentials=True anyway.
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.state.limiter = users.limiter  # slowapi's 429 handler reads app.state.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
