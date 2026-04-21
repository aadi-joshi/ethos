from __future__ import annotations

import json

from app.services.gemini_client import GeminiClient


def generate_bias_explanation(fairness_metrics: dict) -> tuple[str, str]:
    client = GeminiClient()
    prompt = _build_prompt(fairness_metrics)

    if client.is_configured:
        try:
            explanation = client.generate_text(prompt)
            if explanation:
                return explanation, "gemini"
        except Exception:
            pass

    return _fallback_explanation(fairness_metrics), "fallback"



def _build_prompt(fairness_metrics: dict) -> str:
    metrics_json = json.dumps(fairness_metrics, indent=2)

    return (
        "You are an AI fairness auditor. Explain the bias findings clearly for non-technical users. "
        "Use simple language, identify likely causes, and avoid jargon. "
        "Respond in 3-5 concise sentences.\n\n"
        f"Fairness metrics JSON:\n{metrics_json}\n"
    )



def _fallback_explanation(fairness_metrics: dict) -> str:
    overall = fairness_metrics.get("overall_bias", {}) if isinstance(fairness_metrics, dict) else {}
    dpd = float(overall.get("demographic_parity_difference", 0) or 0)
    diratio = float(overall.get("disparate_impact_ratio", 0) or 0)
    fprd = float(overall.get("false_positive_rate_difference", 0) or 0)

    severity = "low"
    if dpd > 0.2 or (0 < diratio < 0.6) or fprd > 0.2:
        severity = "high"
    elif dpd > 0.1 or (0 < diratio < 0.8) or fprd > 0.1:
        severity = "medium"

    return (
        f"The model shows {severity} fairness risk based on the current metrics. "
        f"Outcome rates across groups differ (demographic parity difference: {dpd:.3f}), "
        f"and the selection balance ratio is {diratio:.3f}. "
        f"The false positive rate gap is {fprd:.3f}, which indicates how error burden may differ. "
        "A likely cause is imbalance in historical patterns or threshold settings across groups."
    )
