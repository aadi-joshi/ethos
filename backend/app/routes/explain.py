from fastapi import APIRouter

from app.models.explain import ExplainRequest, ExplainResponse
from app.services.explanation_service import generate_bias_explanation

router = APIRouter(tags=["explanation"])


@router.post("/explain", response_model=ExplainResponse)
def explain_bias(request: ExplainRequest) -> ExplainResponse:
    explanation, source = generate_bias_explanation(request.fairness_metrics)
    return ExplainResponse(explanation=explanation, source=source)
