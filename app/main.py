from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.config import settings
from app.portal.client import PortalClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.portal_client = PortalClient(
        base_url=settings.urja_base_url,
        username=settings.urja_username,
        password=settings.urja_password,
    )

    yield

    app.state.portal_client.close()


app = FastAPI(
    title="Urja Meter API",
    description="Clean API wrapper over the legacy Urja Meter Ops portal.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "Urja Meter API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
app.include_router(router)