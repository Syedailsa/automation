from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
import logging
import uuid

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.core.exceptions import AppException
from app.database import init_db
from app.middleware.rate_limit import RateLimitMiddleware
from app.api import auth, users, notebooks, sources, outputs, agent, ws, tasks
from app.api.v1.router import v1_router
from app.middleware.deprecation import DeprecationHeaderMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield


app = FastAPI(
    title="NotebookLM Portal API",
    description="Multi-user web portal integrating Google NotebookLM with AI agents and browser automation.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# --- Global Exception Handlers ---


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
            }
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    if "invalidly formed UUID" in str(exc) or " badly formed hexadecimal UUID" in str(exc):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": 422,
                    "message": "Invalid UUID format",
                }
            },
        )
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": 400,
                "message": str(exc) or "Invalid input",
            }
        },
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": 409,
                "message": "Resource already exists or constraint violation",
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
            }
        },
    )


# --- CORS ---


app.add_middleware(RequestLoggerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

app.add_middleware(DeprecationHeaderMiddleware)


# --- Routers ---


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notebooks.router)
app.include_router(sources.router)
app.include_router(outputs.router)
app.include_router(agent.router)
app.include_router(ws.router)
app.include_router(tasks.router)
app.include_router(v1_router)


# --- Health Check ---


@app.get("/api/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "ok"}
