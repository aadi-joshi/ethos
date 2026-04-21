from fastapi import FastAPI

from app.routes.health import router as health_router

app = FastAPI(
    title="Ethos AI API",
    version="0.1.0",
    description="Backend API for fairness auditing workflows.",
)

app.include_router(health_router)
