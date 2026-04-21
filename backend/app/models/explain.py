from typing import Any

from pydantic import BaseModel, Field


class ExplainRequest(BaseModel):
    fairness_metrics: dict[str, Any] = Field(default_factory=dict)


class ExplainResponse(BaseModel):
    explanation: str
    source: str
