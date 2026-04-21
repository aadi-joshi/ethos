from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analyze import router as analyze_router
from app.routes.explain import router as explain_router
from app.routes.health import router as health_router
from app.routes.recommend import router as recommend_router
from app.routes.upload import router as upload_router

app = FastAPI(
    title="Ethos AI API",
    version="0.1.0",
    description="Backend API for fairness auditing workflows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(explain_router)
app.include_router(recommend_router)
