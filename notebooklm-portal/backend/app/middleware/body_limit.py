from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Enforce maximum request body size."""

    def __init__(self, app, max_size: int | None = None):
        super().__init__(app)
        self.max_size = max_size or settings.MAX_UPLOAD_SIZE

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_size:
            max_mb = self.max_size // (1024 * 1024)
            return JSONResponse(
                status_code=413,
                content={
                    "error": {
                        "code": 413,
                        "message": f"Request body too large. Maximum size is {max_mb}MB.",
                    }
                },
            )
        return await call_next(request)
