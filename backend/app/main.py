from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analyze import router as analyze_router
from app.routes.citizen import router as citizen_router
from app.routes.explain import router as explain_router
from app.routes.health import router as health_router
from app.routes.probe import router as probe_router
from app.routes.recommend import router as recommend_router
from app.routes.report import router as report_router
from app.routes.reweigh import router as reweigh_router
from app.routes.upload import router as upload_router

app = FastAPI(
    title="Ethos AI API",
    version="2.0.0",
    description=(
        "Ethos AI — India's first accessible LLM bias auditing platform. "
        "Counterfactual probing for caste, gender, religion, and regional bias "
        "in AI systems, plus enhanced ML model fairness auditing."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core routes
app.include_router(health_router)
app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(explain_router)
app.include_router(recommend_router)
app.include_router(report_router)

# New routes
app.include_router(probe_router)
app.include_router(reweigh_router)
app.include_router(citizen_router)
