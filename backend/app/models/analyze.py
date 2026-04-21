from typing import Any

from pydantic import BaseModel


class AnalyzeRequestMetadata(BaseModel):
    target_column: str
    sensitive_attribute: str
    ground_truth_column: str | None = None


class AnalyzeResponse(BaseModel):
    request: AnalyzeRequestMetadata
    group_metrics: dict[str, dict[str, Any]]
    overall_bias: dict[str, float]
    flagged_issues: list[str]
