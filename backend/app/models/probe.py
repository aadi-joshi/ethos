from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class ProbeRunRequest(BaseModel):
    dimension: str                          # caste | religion | gender | region
    domain: str                             # hiring | lending | education | healthcare
    demo_mode: bool = False                 # legacy field, ignored — use target_type
    prompt_template: Optional[str] = None  # user's custom template
    target_url: Optional[str] = None       # external AI endpoint (live_api mode)
    target_type: str = "gemini"            # "gemini" | "sample" | "live_api"
    n_per_group: int = 10
    group_a_key: Optional[str] = None      # override default group pairing
    group_b_key: Optional[str] = None


class DifferentialExample(BaseModel):
    group_a_name: str
    group_a_decision: str
    group_a_reason: str
    group_b_name: str
    group_b_decision: str
    group_b_reason: str


class ProbeResponse(BaseModel):
    dimension: str
    domain: str
    sample_mode: bool
    group_a_key: str
    group_b_key: str
    group_a_label: str
    group_b_label: str
    group_a_count: int
    group_b_count: int
    group_a_acceptance_rate: float
    group_b_acceptance_rate: float
    acceptance_rate_differential: float
    disparate_impact_ratio: float
    sentiment_differential: float
    length_differential: float
    p_value: float
    statistically_significant: bool
    risk_level: str                 # LOW | MEDIUM | HIGH | CRITICAL
    narrative_analysis: str
    differential_examples: list[dict[str, Any]]
    remediation_plan: str
    compliance_assessment: str
    responses_a: list[dict[str, Any]]
    responses_b: list[dict[str, Any]]


class DimensionInfo(BaseModel):
    key: str
    label: str
    description: str
    group_a: dict[str, str]
    group_b: dict[str, str]
