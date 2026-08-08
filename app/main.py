"""FastAPI application factory and top-level route registration."""

from fastapi import FastAPI

from app.api import guidance, predictions
from app.core.config import settings

app = FastAPI(title="Maji Salama AI", version="0.1.0")

app.include_router(predictions.router, prefix="/api")
app.include_router(guidance.router, prefix="/api")

@app.get("/health")
def health_check() -> dict[str, str]:
    """Report process availability and the active application environment."""

    return {"status": "ok", "env": settings.APP_ENV}
