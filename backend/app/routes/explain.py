from fastapi import APIRouter

from app.models.explain import ExplainRequest, ExplainResponse
from app.services.explanation_service import generate_bias_explanation
from app.services.runtime_store import get_runtime_store

router = APIRouter(tags=["explanation"])


@router.post("/explain", response_model=ExplainResponse)
def explain_bias(request: ExplainRequest) -> ExplainResponse:
    explanation, source = generate_bias_explanation(request.fairness_metrics)
    response = ExplainResponse(explanation=explanation, source=source)
    get_runtime_store().latest_explanation = response.model_dump()
    return response
