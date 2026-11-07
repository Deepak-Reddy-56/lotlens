from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, initialise_database
from app.routers.cases import router as cases_router
from app.services.hindsight_service import HindsightService


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialise_database()
    app.state.hindsight = None
    hindsight = None
    if settings.hindsight_api_key:
        hindsight = HindsightService()
        app.state.hindsight = hindsight
    try:
        yield
    finally:
        if hindsight is not None:
            await hindsight.close()
        await engine.dispose()


app = FastAPI(
    title="LotLens API",
    description="Persistent Failure Intelligence for Manufacturing",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "database": "configured",
        "hindsight_configured": bool(settings.hindsight_api_key),
        "bank_id": settings.hindsight_bank_id,
    }


app.include_router(cases_router)
