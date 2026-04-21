from __future__ import annotations

from io import StringIO

import pandas as pd


def load_dataframe_from_bytes(raw_bytes: bytes) -> pd.DataFrame:
    decoded = raw_bytes.decode("utf-8-sig")
    return pd.read_csv(StringIO(decoded))


def validate_required_columns(
    dataframe: pd.DataFrame,
    target_column: str,
    sensitive_attribute: str,
) -> None:
    required = {target_column, sensitive_attribute}
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
