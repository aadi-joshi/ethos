from __future__ import annotations

from app.models.recommend import RecommendationItem


def generate_mitigation_recommendations(
    overall_bias: dict[str, float],
    flagged_issues: list[str],
) -> list[RecommendationItem]:
    recommendations: list[RecommendationItem] = []

    dpd = float(overall_bias.get("demographic_parity_difference", 0) or 0)
    diratio = float(overall_bias.get("disparate_impact_ratio", 0) or 0)
    fprd = float(overall_bias.get("false_positive_rate_difference", 0) or 0)

    if dpd > 0.1 or _has_issue(flagged_issues, "demographic parity"):
        recommendations.append(
            RecommendationItem(
                issue="Uneven positive outcome rates across groups",
                recommendation=(
                    "Rebalance the training dataset with underrepresented groups and "
                    "retrain to reduce outcome disparity."
                ),
                impact="high" if dpd > 0.2 else "medium",
            )
        )

    if 0 < diratio < 0.8 or _has_issue(flagged_issues, "disparate impact"):
        recommendations.append(
            RecommendationItem(
                issue="Disparate impact ratio below fairness threshold",
                recommendation=(
                    "Adjust decision thresholds per validation analysis and evaluate "
                    "fairness-constrained training objectives."
                ),
                impact="high" if diratio < 0.6 else "medium",
            )
        )

    if fprd > 0.1 or _has_issue(flagged_issues, "false positive"):
        recommendations.append(
            RecommendationItem(
                issue="False positive error burden differs across groups",
                recommendation=(
                    "Calibrate model outputs and tune classification thresholds to "
                    "equalize false positive rates across sensitive groups."
                ),
                impact="high" if fprd > 0.2 else "medium",
            )
        )

    if not recommendations:
        recommendations.append(
            RecommendationItem(
                issue="No severe fairness issues detected",
                recommendation=(
                    "Continue monitoring fairness metrics over time and run periodic "
                    "audits as new data is collected."
                ),
                impact="low",
            )
        )

    recommendations.append(
        RecommendationItem(
            issue="Sensitive feature leakage risk",
            recommendation=(
                "Test models with and without sensitive proxies to verify that "
                "protected attributes are not indirectly driving outcomes."
            ),
            impact="medium",
        )
    )

    return recommendations



def _has_issue(flagged_issues: list[str], keyword: str) -> bool:
    needle = keyword.lower()
    return any(needle in issue.lower() for issue in flagged_issues)
