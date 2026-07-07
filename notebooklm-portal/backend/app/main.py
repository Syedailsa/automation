import time
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

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
from app.database import init_db, engine
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.metrics import MetricsMiddleware, metrics_collector
from app.api import auth, users, notebooks, sources, outputs, agent, ws, tasks
from app.api.v1.router import v1_router
from app.middleware.deprecation import DeprecationHeaderMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware
from app.middleware.body_limit import BodySizeLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.services.cache_service import cache
from app.services.task_manager import task_manager

app_start_time: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global app_start_time
    app_start_time = time.time()

    await init_db()
    await cache.initialize()
    logging.getLogger(__name__).info("Application started")
    yield

    # Graceful shutdown
    logging.getLogger(__name__).info("Shutting down...")

    # Cancel pending background tasks
    pending = [t for t in task_manager._asyncio_tasks.values() if not t.done()]
    if pending:
        logging.getLogger(__name__).info(f"Cancelling {len(pending)} pending tasks")
        for task in pending:
            task.cancel()
        import asyncio
        await asyncio.gather(*pending, return_exceptions=True)

    # Close cache (Redis connection)
    await cache.close()

    # Dispose database engine pool
    await engine.dispose()

    logging.getLogger(__name__).info("Shutdown complete")


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


# --- Middleware (order matters: last added = first executed) ---

app.add_middleware(RequestLoggerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(BodySizeLimitMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(RateLimitMiddleware, window_seconds=3600)
app.add_middleware(DeprecationHeaderMiddleware)

from starlette.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=500)


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
async def health_check() -> dict:
    """Health check endpoint with DB and Redis ping."""
    uptime = time.time() - app_start_time if app_start_time else 0

    # Check database
    db_ok = True
    try:
        from sqlalchemy import text

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    # Check cache
    cache_info = await cache.health_check()

    healthy = db_ok and cache_info.get("healthy", False)
    status_code = 200 if healthy else 503

    result = {
        "status": "ok" if healthy else "degraded",
        "uptime_seconds": round(uptime, 1),
        "database": {"healthy": db_ok},
        "cache": cache_info,
    }

    if not healthy:
        return JSONResponse(status_code=status_code, content=result)
    return result


# --- API Metrics ---


@app.get("/api/metrics", tags=["metrics"])
async def get_metrics() -> dict:
    """API metrics endpoint for monitoring."""
    uptime = time.time() - app_start_time if app_start_time else 0
    return metrics_collector.get_metrics({}, uptime)
