from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from src.api.db import close_db, init_db
from src.api.metrics import PrometheusMiddleware, get_metrics
from src.api.routes import analysis, campaigns, feedback, webhook, stream


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Social Manipulation Detector Agent",
        description="AI-powered psychological manipulation & fake news shield for social platforms",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(PrometheusMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(analysis.router)
    app.include_router(campaigns.router)
    app.include_router(feedback.router)
    app.include_router(webhook.router)
    app.include_router(stream.router)

    @app.get("/health")
    async def health():
        from src.model_availability import get_readiness_report
        return {
            "status": "ok",
            "version": "0.1.0",
            "readiness": get_readiness_report(),
        }

    @app.get("/metrics")
    async def metrics():
        return Response(content=get_metrics(), media_type="text/plain")

    return app


app = create_app()


def main() -> None:
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
