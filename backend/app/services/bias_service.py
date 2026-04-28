from __future__ import annotations

from io import StringIO

import pandas as pd

POSITIVE_TOKENS = {"1", "1.0", "true", "yes", "positive", "approved"}
NEGATIVE_TOKENS = {"0", "0.0", "false", "no", "negative", "rejected"}


def load_dataframe_from_bytes(raw_bytes: bytes) -> pd.DataFrame:
    decoded = raw_bytes.decode("utf-8-sig")
    return pd.read_csv(StringIO(decoded), sep=None, engine="python")


def validate_required_columns(
    dataframe: pd.DataFrame,
    required_columns: list[str],
) -> None:
    required = set(required_columns)
    missing = [column for column in required if column not in dataframe.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required column(s): {missing_text}")


def validate_binary_like_column(dataframe: pd.DataFrame, column_name: str) -> None:
    series = dataframe[column_name]

    if series.isna().any():
        raise ValueError(
            f"Column '{column_name}' contains missing values. Fill null values before analysis."
        )

    normalized = _normalize_series(series)
    allowed_values = POSITIVE_TOKENS | NEGATIVE_TOKENS
    invalid_values = sorted(set(normalized[~normalized.isin(allowed_values)].tolist()))

    if invalid_values:
        preview = ", ".join(invalid_values[:5])
        raise ValueError(
            f"Column '{column_name}' must be binary-like (0/1, true/false, yes/no). Invalid values: {preview}"
        )


def validate_sensitive_attribute(dataframe: pd.DataFrame, column_name: str) -> None:
    series = dataframe[column_name]

    if series.isna().any():
        raise ValueError(
            f"Sensitive attribute '{column_name}' contains missing values. Fill null values before analysis."
        )

    unique_count = int(series.nunique(dropna=True))
    if unique_count < 2:
        raise ValueError(
            f"Sensitive attribute '{column_name}' must contain at least two distinct groups."
        )


def calculate_selection_rate_by_group(
    dataframe: pd.DataFrame,
    target_column: str,
    sensitive_attribute: str,
) -> dict[str, dict[str, float]]:
    working = dataframe[[sensitive_attribute, target_column]].assign(
        __positive=_to_positive_series(dataframe[target_column])
    )

    grouped = (
        working.groupby(sensitive_attribute, dropna=False)["__positive"]
        .agg(["count", "sum"])
        .reset_index()
    )

    results: dict[str, dict[str, float]] = {}
    for _, row in grouped.iterrows():
        total = float(row["count"])
        positives = float(row["sum"])
        selection_rate = positives / total if total > 0 else 0.0
        results[str(row[sensitive_attribute])] = {
            "count": total,
            "positive_outcomes": positives,
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
    return int(normalized in POSITIVE_TOKENS)


def _to_positive_series(series: pd.Series) -> pd.Series:
    normalized = _normalize_series(series)
    return normalized.isin(POSITIVE_TOKENS).astype(int)


def _normalize_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower()


def calculate_false_positive_rate_by_group(
    dataframe: pd.DataFrame,
    prediction_column: str,
    label_column: str,
    sensitive_attribute: str,
) -> dict[str, float]:
    working = dataframe[[sensitive_attribute, prediction_column, label_column]].assign(
        __pred_positive=_to_positive_series(dataframe[prediction_column]),
        __label_positive=_to_positive_series(dataframe[label_column]),
    )

    actual_negative = working[working["__label_positive"] == 0]
    if actual_negative.empty:
        groups = dataframe[sensitive_attribute].drop_duplicates().tolist()
        return {str(group): 0.0 for group in groups}

    grouped = (
        actual_negative.groupby(sensitive_attribute, dropna=False)["__pred_positive"]
        .agg(["count", "sum"])
        .reset_index()
    )

    results: dict[str, float] = {
        str(group): 0.0 for group in dataframe[sensitive_attribute].drop_duplicates().tolist()
    }

    for _, row in grouped.iterrows():
        total_negative = float(row["count"])
        false_positive_count = float(row["sum"])
        results[str(row[sensitive_attribute])] = (
            false_positive_count / total_negative if total_negative > 0 else 0.0
        )

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


# ---------------------------------------------------------------------------
# Additional metrics (research standard set — 6 total)
# ---------------------------------------------------------------------------

def calculate_true_positive_rate_by_group(
    dataframe: pd.DataFrame,
    prediction_column: str,
    label_column: str,
    sensitive_attribute: str,
) -> dict[str, float]:
    """True Positive Rate (Recall) per group. Required for AOD and EOD."""
    working = dataframe[[sensitive_attribute, prediction_column, label_column]].assign(
        __pred_positive=_to_positive_series(dataframe[prediction_column]),
        __label_positive=_to_positive_series(dataframe[label_column]),
    )
    actual_positive = working[working["__label_positive"] == 1]
    if actual_positive.empty:
        return {str(g): 0.0 for g in dataframe[sensitive_attribute].unique()}

    grouped = (
        actual_positive.groupby(sensitive_attribute, dropna=False)["__pred_positive"]
        .agg(["count", "sum"])
        .reset_index()
    )
    results: dict[str, float] = {
        str(g): 0.0 for g in dataframe[sensitive_attribute].drop_duplicates()
    }
    for _, row in grouped.iterrows():
        total = float(row["count"])
        tp = float(row["sum"])
        results[str(row[sensitive_attribute])] = tp / total if total > 0 else 0.0
    return results


def calculate_equal_opportunity_difference(
    true_positive_rates: dict[str, float],
) -> float:
    """
    Equal Opportunity Difference: max(TPR) - min(TPR).
    Measures whether the model gives equally high recall across groups.
    Ideal value: 0. Threshold: > 0.1 flagged.
    """
    rates = list(true_positive_rates.values())
    if not rates:
        return 0.0
    return max(rates) - min(rates)


def calculate_average_odds_difference(
    false_positive_rates: dict[str, float],
    true_positive_rates: dict[str, float],
) -> float:
    """
    Average Odds Difference: average of FPR diff and TPR diff.
    The gold standard for 'equalized odds' fairness.
    Ideal value: 0. Threshold: > 0.1 flagged.
    """
    fpr_vals = list(false_positive_rates.values())
    tpr_vals = list(true_positive_rates.values())
    if not fpr_vals or not tpr_vals:
        return 0.0
    fpr_diff = max(fpr_vals) - min(fpr_vals)
    tpr_diff = max(tpr_vals) - min(tpr_vals)
    return (fpr_diff + tpr_diff) / 2.0


def calculate_theil_index(
    group_metrics: dict[str, dict[str, float]],
) -> float:
    """
    Theil Index (entropy-based inequality measure).
    Captures both between-group and within-group variation.
    Ideal value: 0. Any positive value indicates inequality.
    """
    import math

    rates = [m["selection_rate"] for m in group_metrics.values() if m["selection_rate"] > 0]
    if not rates:
        return 0.0

    mu = sum(rates) / len(rates)
    if mu == 0:
        return 0.0

    theil = sum((r / mu) * math.log(r / mu) for r in rates if r > 0)
    return max(0.0, theil / len(rates))


def build_flagged_issues_extended(
    dpd: float,
    dir_ratio: float,
    fpr_diff: float,
    eod: float,
    aod: float,
    theil: float,
) -> list[str]:
    """Extended issue detection covering all 6 metrics."""
    issues: list[str] = []
    if dpd > 0.1:
        issues.append("High demographic parity difference detected.")
    if 0 < dir_ratio < 0.8:
        issues.append("Disparate impact ratio is below the 80% fairness threshold.")
    if fpr_diff > 0.1:
        issues.append("False positive rates differ significantly across groups.")
    if eod > 0.1:
        issues.append("Equal opportunity difference is high — recall is unequal across groups.")
    if aod > 0.1:
        issues.append("Average odds difference exceeds threshold — equalized odds not satisfied.")
    if theil > 0.05:
        issues.append("Theil Index indicates significant between-group outcome inequality.")
    return issues
