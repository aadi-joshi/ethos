from typing import Any

from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    overall_bias: dict[str, float] = Field(default_factory=dict)
    flagged_issues: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecommendationItem(BaseModel):
    issue: str
    recommendation: str
    impact: str


class RecommendResponse(BaseModel):
    recommendations: list[RecommendationItem]
