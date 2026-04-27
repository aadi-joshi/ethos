from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class CitizenReportRequest(BaseModel):
    domain: str                         # hiring | lending | education | healthcare | other
    bias_type: str                      # caste | religion | gender | region | age | other
    description: str                    # what happened
    state: Optional[str] = None         # Indian state where incident occurred
    organization_type: Optional[str] = None  # bank | employer | education | hospital | other
    impact: Optional[str] = None        # how it affected you
    consent_to_aggregate: bool = True


class CitizenReportResponse(BaseModel):
    report_id: str
    preliminary_assessment: str
    resources: list[dict[str, str]]
    message: str
