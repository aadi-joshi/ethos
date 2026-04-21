from fastapi import APIRouter

from app.models.recommend import RecommendRequest, RecommendResponse
from app.services.mitigation_service import generate_mitigation_recommendations
from app.services.runtime_store import get_runtime_store

router = APIRouter(tags=["recommendation"])


@router.post("/recommend", response_model=RecommendResponse)
def recommend_mitigation(request: RecommendRequest) -> RecommendResponse:
    recommendations = generate_mitigation_recommendations(
        overall_bias=request.overall_bias,
        flagged_issues=request.flagged_issues,
    )
    response = RecommendResponse(recommendations=recommendations)
    get_runtime_store().latest_recommendations = response.model_dump()
    return response
