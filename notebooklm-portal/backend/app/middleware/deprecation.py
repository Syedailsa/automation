from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class DeprecationHeaderMiddleware(BaseHTTPMiddleware):
    """Adds deprecation headers to old /api/ (non-v1) endpoints."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        path = request.url.path
        if path.startswith("/api/") and not path.startswith("/api/v1/") and not path.startswith("/api/health"):
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = "2026-12-31"
            response.headers["Link"] = f"</api/v1{path}>; rel=\"successor-version\""

        return response
