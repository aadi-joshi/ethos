"""
Kamiran & Calders (2012) reweighing — a pre-processing bias mitigation algorithm.

Reference: Kamiran, F., & Calders, T. (2012). Data preprocessing techniques for
classification without discrimination. Knowledge and Information Systems, 33(1), 1-33.

Given a dataset, assigns sample weights such that when used during model training,
the weighted dataset satisfies demographic parity without changing any labels.
The corrected CSV with a 'sample_weight' column can be exported by users.
"""

from __future__ import annotations

import io
from typing import Optional

import pandas as pd


def apply_reweighing(
    df: pd.DataFrame,
    target_col: str,
    sensitive_attr: str,
) -> tuple[pd.DataFrame, dict]:
    """
    Compute Kamiran-Calders sample weights and return augmented dataframe.

    Returns:
        (augmented_df, summary): augmented_df has a new 'sample_weight' column;
        summary contains before/after metrics for display.
    """
    df = df.copy()
    total = len(df)

    # Compute expected (independent) probabilities
    p_positive = (df[target_col].astype(str).str.strip().str.lower()
                  .isin({"1", "1.0", "true", "yes", "positive", "approved"}).sum() / total)

    group_probs: dict[str, dict[str, float]] = {}
    for group_val, group_df in df.groupby(sensitive_attr, dropna=False):
        group_key = str(group_val)
        n_group = len(group_df)
        p_group = n_group / total

        pos_mask = group_df[target_col].astype(str).str.strip().str.lower().isin(
            {"1", "1.0", "true", "yes", "positive", "approved"}
        )
        n_pos = pos_mask.sum()
        n_neg = n_group - n_pos
        p_pos_given_group = n_pos / n_group if n_group > 0 else 0.0

        # Expected counts under independence (fairness ideal)
        exp_pos = p_positive * p_group * total
        exp_neg = (1 - p_positive) * p_group * total

        # Weights: w(group, outcome) = expected_count / actual_count
        w_pos = (exp_pos / n_pos) if n_pos > 0 else 1.0
        w_neg = (exp_neg / n_neg) if n_neg > 0 else 1.0

        group_probs[group_key] = {
            "n_total": n_group,
            "n_positive": int(n_pos),
            "selection_rate_before": round(p_pos_given_group, 4),
            "weight_positive": round(w_pos, 4),
            "weight_negative": round(w_neg, 4),
        }

    # Assign weights row-by-row
    def _get_weight(row: pd.Series) -> float:
        group_key = str(row[sensitive_attr])
        is_positive = str(row[target_col]).strip().lower() in {
            "1", "1.0", "true", "yes", "positive", "approved"
        }
        group_data = group_probs.get(group_key, {})
        return group_data.get("weight_positive" if is_positive else "weight_negative", 1.0)

    df["sample_weight"] = df.apply(_get_weight, axis=1)

    # Verify: weighted selection rates should be approximately equal across groups
    expected_rates: dict[str, float] = {}
    for group_val, group_df in df.groupby(sensitive_attr, dropna=False):
        group_key = str(group_val)
        pos_mask = group_df[target_col].astype(str).str.strip().str.lower().isin(
            {"1", "1.0", "true", "yes", "positive", "approved"}
        )
        weighted_total = group_df["sample_weight"].sum()
        weighted_positive = group_df.loc[pos_mask, "sample_weight"].sum()
        rate = (weighted_positive / weighted_total) if weighted_total > 0 else 0.0
        expected_rates[group_key] = round(rate, 4)
        group_probs[group_key]["selection_rate_after"] = round(rate, 4)

    summary = {
        "algorithm": "Kamiran & Calders (2012) Reweighing",
        "groups": group_probs,
        "interpretation": (
            "The 'sample_weight' column contains per-row training weights. "
            "Pass these as the 'sample_weight' parameter when calling model.fit() "
            "(sklearn, XGBoost, LightGBM all support this). "
            "The reweighed dataset satisfies demographic parity without altering labels."
        ),
    }

    return df, summary


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")
