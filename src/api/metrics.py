from __future__ import annotations

import time
from collections.abc import Callable

from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


try:
    from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY
    _METRICS_AVAILABLE = True
except ImportError:
    _METRICS_AVAILABLE = False


if _METRICS_AVAILABLE:
    REQUEST_COUNT = Counter(
        "smda_http_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "smda_http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "endpoint"],
        buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    )
    VERDICT_COUNT = Counter(
        "smda_verdicts_total",
        "Total verdicts produced",
        ["level", "platform"],
    )
    MANIPULATION_INDEX = Histogram(
        "smda_manipulation_index",
        "Distribution of manipulation index scores",
        buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    )
    LLM_COST = Gauge(
        "smda_llm_cost_total_usd",
        "Total LLM API cost in USD",
    )
    LLM_CALLS = Counter(
        "smda_llm_calls_total",
        "Total LLM API calls",
        ["model"],
    )
    CACHE_HIT_RATIO = Gauge(
        "smda_cache_hit_ratio",
        "Redis verdict cache hit ratio",
    )
    PIPELINE_LATENCY = Histogram(
        "smda_pipeline_duration_seconds",
        "Full analysis pipeline latency per comment",
        buckets=[0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 15.0],
    )
    ACTIVE_CAMPAIGNS = Gauge(
        "smda_active_campaigns",
        "Number of currently active manipulation campaigns",
    )


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not _METRICS_AVAILABLE:
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        elapsed = time.time() - start_time

        endpoint = request.url.path
        method = request.method

        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(elapsed)

        return response


def record_verdict(level: str, platform: str) -> None:
    if _METRICS_AVAILABLE:
        VERDICT_COUNT.labels(level=level, platform=platform).inc()


def record_manipulation_score(score: float) -> None:
    if _METRICS_AVAILABLE:
        MANIPULATION_INDEX.observe(score)


def record_llm_call(model: str, cost: float) -> None:
    if _METRICS_AVAILABLE:
        LLM_CALLS.labels(model=model).inc()
        current = LLM_COST._value.get()
        LLM_COST.set((current or 0.0) + cost)


def update_cache_ratio(ratio: float) -> None:
    if _METRICS_AVAILABLE:
        CACHE_HIT_RATIO.set(ratio)


def record_pipeline_latency(seconds: float) -> None:
    if _METRICS_AVAILABLE:
        PIPELINE_LATENCY.observe(seconds)


def update_active_campaigns(count: int) -> None:
    if _METRICS_AVAILABLE:
        ACTIVE_CAMPAIGNS.set(count)


def get_metrics() -> bytes:
    if not _METRICS_AVAILABLE:
        return b"# prometheus_client not installed\n"
    return generate_latest(REGISTRY)
