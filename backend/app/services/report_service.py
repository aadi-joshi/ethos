from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status

from app.models.report import ReportPayload, ReportResponse, ReportSummary
from app.services.runtime_store import get_runtime_store



def generate_report() -> ReportResponse:
    store = get_runtime_store()

    if not store.latest_analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analysis data found. Run /analyze before generating report.",
        )

    overall_bias = store.latest_analysis.get("overall_bias", {})
    flagged_issues = store.latest_analysis.get("flagged_issues", [])
    explanation = _extract_explanation(store.latest_explanation)
    recommendations = _extract_recommendations(store.latest_recommendations)

    generated_at = datetime.now(UTC).isoformat()
    report_id = f"report-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"

    payload = ReportPayload(
        summary=ReportSummary(
            risk_level=_derive_risk_level(overall_bias, flagged_issues),
            generated_at=generated_at,
        ),
        metrics=store.latest_analysis,
        explanation=explanation,
        recommendations=recommendations,
    )

    file_path = _persist_report(report_id, payload.model_dump())

    return ReportResponse(
        report_id=report_id,
        report=payload,
        file_path=file_path,
    )



def _derive_risk_level(overall_bias: dict[str, Any], flagged_issues: list[str]) -> str:
    dpd = float(overall_bias.get("demographic_parity_difference", 0) or 0)
    diratio = float(overall_bias.get("disparate_impact_ratio", 0) or 0)
    fprd = float(overall_bias.get("false_positive_rate_difference", 0) or 0)

    if dpd > 0.2 or (0 < diratio < 0.6) or fprd > 0.2 or len(flagged_issues) >= 3:
        return "high"
    if dpd > 0.1 or (0 < diratio < 0.8) or fprd > 0.1 or len(flagged_issues) >= 1:
        return "medium"
    return "low"



def _extract_explanation(explanation_payload: dict[str, Any] | None) -> str:
    if not explanation_payload:
        return "Explanation not generated yet. Run /explain with the latest fairness metrics."

    return str(explanation_payload.get("explanation", "No explanation available."))



def _extract_recommendations(recommend_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not recommend_payload:
        return [
            {
                "issue": "Recommendations not generated",
                "recommendation": "Run /recommend using the latest bias analysis output.",
                "impact": "low",
            }
        ]

    recommendations = recommend_payload.get("recommendations", [])
    if not isinstance(recommendations, list):
        return []
    return recommendations



def _persist_report(report_id: str, payload: dict[str, Any]) -> str:
    reports_dir = Path(__file__).resolve().parents[3] / "reports" / "generated"
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_file = reports_dir / f"{report_id}.json"
    report_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return str(report_file)
