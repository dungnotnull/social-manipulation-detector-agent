from __future__ import annotations

from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, Request
from neo4j import AsyncGraphDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db import get_db as _get_db
from src.config import settings

_redis_pool: aioredis.Redis | None = None
_neo4j_driver = None


async def get_redis() -> aioredis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_pool


async def get_neo4j():
    global _neo4j_driver
    if _neo4j_driver is None:
        _neo4j_driver = AsyncGraphDatabase.driver(
            settings.neo4j_url,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _neo4j_driver


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in _get_db():
        yield session


class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def check(self, request: Request) -> None:
        redis_client = await get_redis()
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"

        current = await redis_client.get(key)
        if current is None:
            await redis_client.setex(key, self.window_seconds, 1)
        elif int(current) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        else:
            await redis_client.incr(key)


rate_limiter = RateLimiter(
    max_requests=settings.api_rate_limit_per_min,
    window_seconds=60,
)
