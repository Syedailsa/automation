import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.core.security import verify_token


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-user tier-based rate limiting.

    Tiers:
      - admin: unlimited (RATE_LIMIT_ADMIN = 0)
      - pro:   200 requests/hour
      - free:  50 requests/hour
      - anon:  30 requests/hour (by IP)
    """

    ANON_LIMIT = 30

    TIER_LIMITS = {
        "admin": settings.RATE_LIMIT_ADMIN,
        "pro": settings.RATE_LIMIT_PRO,
        "free": settings.RATE_LIMIT_FREE,
    }

    def __init__(self, app, window_seconds: int = 3600):
        super().__init__(app)
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_info(self, request: Request) -> tuple[str, str]:
        """Return (client_id, tier) from JWT or IP."""
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
            payload = verify_token(token)
            if payload:
                user_id = payload.get("sub", "unknown")
                role = payload.get("role", "free")
                return f"user:{user_id}", role

        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        return f"ip:{ip}", "anon"

    def _get_limit(self, tier: str) -> int:
        if tier == "anon":
            return self.ANON_LIMIT
        return self.TIER_LIMITS.get(tier, self.TIER_LIMITS["free"])

    def _clean_old_requests(self, client_id: str):
        now = time.time()
        self._requests[client_id] = [
            t
            for t in self._requests[client_id]
            if now - t < self.window_seconds
        ]

    async def dispatch(self, request: Request, call_next):
        if request.url.path in (
            "/api/health",
            "/api/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ):
            return await call_next(request)

        client_id, tier = self._get_client_info(request)
        limit = self._get_limit(tier)

        # Unlimited tier
        if limit == 0:
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = "unlimited"
            response.headers["X-RateLimit-Tier"] = tier
            response.headers["X-RateLimit-Remaining"] = "unlimited"
            return response

        self._clean_old_requests(client_id)
        now = time.time()
        recent = [t for t in self._requests[client_id] if now - t < self.window_seconds]
        self._requests[client_id] = recent

        if len(recent) >= limit:
            retry_after = int(self.window_seconds - (now - recent[0]))
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": 429,
                        "message": f"Rate limit exceeded for {tier} tier. Try again later.",
                        "tier": tier,
                        "limit": limit,
                        "window_seconds": self.window_seconds,
                    }
                },
                headers={
                    "Retry-After": str(max(1, retry_after)),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Tier": tier,
                },
            )

        self._requests[client_id].append(now)
        remaining = limit - len(self._requests[client_id])

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Tier"] = tier
        return response
