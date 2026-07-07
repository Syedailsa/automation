import time
import logging
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Tracks request count, latency, and status codes per endpoint."""

    def __init__(self, app):
        super().__init__(app)
        self._metrics: dict[str, dict] = defaultdict(
            lambda: {"count": 0, "total_latency_ms": 0.0, "status_codes": defaultdict(int)}
        )
        self._start_time = time.time()

    def _normalize_path(self, path: str) -> str:
        """Normalize path by replacing UUIDs and IDs with placeholders."""
        parts = path.strip("/").split("/")
        normalized = []
        for part in parts:
            if len(part) == 36 and part.count("-") == 4:
                normalized.append("{id}")
            elif part.isdigit():
                normalized.append("{id}")
            else:
                normalized.append(part)
        return "/" + "/".join(normalized)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/api/metrics", "/api/health"):
            return await call_next(request)

        method = request.method
        path = self._normalize_path(request.url.path)
        endpoint = f"{method} {path}"

        start = time.time()
        response = await call_next(request)
        latency_ms = (time.time() - start) * 1000

        m = self._metrics[endpoint]
        m["count"] += 1
        m["total_latency_ms"] += latency_ms
        m["status_codes"][response.status_code] += 1

        response.headers["X-Response-Time"] = f"{latency_ms:.1f}ms"
        return response


class MetricsCollector:
    """Collects and exposes API metrics."""

    def __init__(self):
        self._request_count: int = 0
        self._error_count: int = 0
        self._latencies: list[float] = []

    def record_request(self, latency_ms: float, status_code: int):
        self._request_count += 1
        self._latencies.append(latency_ms)
        if status_code >= 400:
            self._error_count += 1
        # Keep last 1000 latencies
        if len(self._latencies) > 1000:
            self._latencies = self._latencies[-1000:]

    def get_metrics(self, middleware_metrics: dict, uptime_seconds: float) -> dict:
        latencies = self._latencies or [0]
        return {
            "uptime_seconds": round(uptime_seconds, 1),
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "error_rate": round(
                self._error_count / max(1, self._request_count) * 100, 2
            ),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
            "p50_latency_ms": round(sorted(latencies)[len(latencies) // 2], 2),
            "p95_latency_ms": round(
                sorted(latencies)[int(len(latencies) * 0.95)], 2
            ),
            "p99_latency_ms": round(
                sorted(latencies)[int(len(latencies) * 0.99)], 2
            ),
            "endpoints": dict(middleware_metrics),
        }


metrics_collector = MetricsCollector()
