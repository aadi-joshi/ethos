from typing import Any

from pydantic import BaseModel, Field


class ReportSummary(BaseModel):
    risk_level: str
    generated_at: str


class ReportPayload(BaseModel):
    summary: ReportSummary
    metrics: dict[str, Any] = Field(default_factory=dict)
    explanation: str
    recommendations: list[dict[str, Any]] = Field(default_factory=list)


class ReportResponse(BaseModel):
    report_id: str
    report: ReportPayload
    file_path: str
