from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import get_settings
from app.core.logging import setup_logging
from app.schemas import HealthResponse
from app.scheduler import SchedulerManager
from app.services.container import ServiceContainer

settings = get_settings()
setup_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = ServiceContainer(settings)
    await container.startup()
    scheduler = SchedulerManager(settings=settings, devotional_service=container.devotional_service)
    scheduler.start()
    app.state.container = container
    app.state.scheduler = scheduler
    try:
        yield
    finally:
        scheduler.shutdown()
        await container.shutdown()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    docs_url="/docs" if settings.expose_docs else None,
    redoc_url="/redoc" if settings.expose_docs else None,
    openapi_url="/openapi.json" if settings.expose_docs else None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name)
