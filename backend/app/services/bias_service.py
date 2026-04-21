from __future__ import annotations

from io import StringIO

import pandas as pd


def load_dataframe_from_bytes(raw_bytes: bytes) -> pd.DataFrame:
    decoded = raw_bytes.decode("utf-8-sig")
    return pd.read_csv(StringIO(decoded))


def validate_required_columns(
    dataframe: pd.DataFrame,
    required_columns: list[str],
) -> None:
    required = set(required_columns)
    missing = [column for column in required if column not in dataframe.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required column(s): {missing_text}")


def calculate_selection_rate_by_group(
    dataframe: pd.DataFrame,
    target_column: str,
    sensitive_attribute: str,
) -> dict[str, dict[str, float]]:
    results: dict[str, dict[str, float]] = {}

    for group_value, group_frame in dataframe.groupby(sensitive_attribute, dropna=False):
        total = len(group_frame)
        positives = int(group_frame[target_column].apply(_is_positive).sum())
        selection_rate = positives / total if total > 0 else 0.0
        results[str(group_value)] = {
            "count": float(total),
            "positive_outcomes": float(positives),
            "selection_rate": selection_rate,
        }

    return results


def calculate_demographic_parity_difference(
    group_metrics: dict[str, dict[str, float]],
) -> float:
    rates = [metrics["selection_rate"] for metrics in group_metrics.values()]
    if not rates:
        return 0.0
    return max(rates) - min(rates)


def calculate_disparate_impact_ratio(
    group_metrics: dict[str, dict[str, float]],
) -> float:
    rates = [metrics["selection_rate"] for metrics in group_metrics.values()]
    positive_rates = [rate for rate in rates if rate > 0]

    if len(positive_rates) < 2:
        return 0.0

    return min(positive_rates) / max(positive_rates)


def _is_positive(value: object) -> int:
    normalized = str(value).strip().lower()
    return int(normalized in {"1", "1.0", "true", "yes", "positive", "approved"})


def calculate_false_positive_rate_by_group(
    dataframe: pd.DataFrame,
    prediction_column: str,
    label_column: str,
    sensitive_attribute: str,
) -> dict[str, float]:
    results: dict[str, float] = {}

    for group_value, group_frame in dataframe.groupby(sensitive_attribute, dropna=False):
        actual_negative_mask = group_frame[label_column].apply(_is_positive) == 0
        actual_negative_frame = group_frame[actual_negative_mask]

        if len(actual_negative_frame) == 0:
            results[str(group_value)] = 0.0
            continue

        false_positive_count = int(
            actual_negative_frame[prediction_column].apply(_is_positive).sum()
        )
        results[str(group_value)] = false_positive_count / len(actual_negative_frame)

    return results


def calculate_false_positive_rate_difference(
    false_positive_rates: dict[str, float],
) -> float:
    rates = list(false_positive_rates.values())
    if not rates:
        return 0.0
    return max(rates) - min(rates)


def build_flagged_issues(
    demographic_parity_difference: float,
    disparate_impact_ratio: float,
    false_positive_rate_difference: float,
) -> list[str]:
    issues: list[str] = []

    if demographic_parity_difference > 0.1:
        issues.append("High demographic parity difference detected.")

    if 0 < disparate_impact_ratio < 0.8:
        issues.append("Disparate impact ratio is below the 80% fairness threshold.")

    if false_positive_rate_difference > 0.1:
        issues.append("False positive rates differ significantly across groups.")

    return issues
