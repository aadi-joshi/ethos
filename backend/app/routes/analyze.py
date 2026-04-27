from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.models.analyze import AnalyzeRequestMetadata, AnalyzeResponse
from app.services.bias_service import (
    build_flagged_issues_extended,
    calculate_average_odds_difference,
    calculate_demographic_parity_difference,
    calculate_disparate_impact_ratio,
    calculate_equal_opportunity_difference,
    calculate_false_positive_rate_by_group,
    calculate_false_positive_rate_difference,
    calculate_selection_rate_by_group,
    calculate_theil_index,
    calculate_true_positive_rate_by_group,
    load_dataframe_from_bytes,
    validate_binary_like_column,
    validate_required_columns,
    validate_sensitive_attribute,
)
from app.services.runtime_store import get_runtime_store

router = APIRouter(tags=["analysis"])


@router.post("/analyze")
async def analyze_bias(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    sensitive_attribute: str = Form(...),
    ground_truth_column: str | None = Form(default=None),
) -> AnalyzeResponse:
    if not target_column.strip():
        raise HTTPException(status_code=400, detail="target_column is required.")
    if not sensitive_attribute.strip():
        raise HTTPException(status_code=400, detail="sensitive_attribute is required.")
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a valid CSV file.")

    try:
        raw_bytes = await file.read()
        if not raw_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        dataframe = load_dataframe_from_bytes(raw_bytes)
        if dataframe.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty.")

        label_column = ground_truth_column or target_column
        validate_required_columns(dataframe, [target_column, sensitive_attribute, label_column])
        validate_binary_like_column(dataframe, target_column)
        validate_binary_like_column(dataframe, label_column)
        validate_sensitive_attribute(dataframe, sensitive_attribute)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=400, detail="Invalid CSV input for analysis.") from error

    # Core selection-rate metrics
    group_metrics = calculate_selection_rate_by_group(
        dataframe, target_column=target_column, sensitive_attribute=sensitive_attribute
    )

    # FPR per group (needs ground truth)
    fpr_by_group = calculate_false_positive_rate_by_group(
        dataframe,
        prediction_column=target_column,
        label_column=ground_truth_column or target_column,
        sensitive_attribute=sensitive_attribute,
    )

    # TPR per group (needed for EOD and AOD)
    tpr_by_group = calculate_true_positive_rate_by_group(
        dataframe,
        prediction_column=target_column,
        label_column=ground_truth_column or target_column,
        sensitive_attribute=sensitive_attribute,
    )

    # Enrich per-group metrics
    enriched_group_metrics = {
        group: {
            **metrics,
            "false_positive_rate": fpr_by_group.get(group, 0.0),
            "true_positive_rate": tpr_by_group.get(group, 0.0),
        }
        for group, metrics in group_metrics.items()
    }

    # Aggregate metrics
    dpd = calculate_demographic_parity_difference(group_metrics)
    dir_ratio = calculate_disparate_impact_ratio(group_metrics)
    fpr_diff = calculate_false_positive_rate_difference(fpr_by_group)
    eod = calculate_equal_opportunity_difference(tpr_by_group)
    aod = calculate_average_odds_difference(fpr_by_group, tpr_by_group)
    theil = calculate_theil_index(group_metrics)

    flagged_issues = build_flagged_issues_extended(
        dpd=dpd,
        dir_ratio=dir_ratio,
        fpr_diff=fpr_diff,
        eod=eod,
        aod=aod,
        theil=theil,
    )

    response = AnalyzeResponse(
        request=AnalyzeRequestMetadata(
            target_column=target_column,
            sensitive_attribute=sensitive_attribute,
            ground_truth_column=ground_truth_column,
        ),
        group_metrics=enriched_group_metrics,
        overall_bias={
            "demographic_parity_difference": dpd,
            "disparate_impact_ratio": dir_ratio,
            "false_positive_rate_difference": fpr_diff,
            "equal_opportunity_difference": eod,
            "average_odds_difference": aod,
            "theil_index": theil,
        },
        flagged_issues=flagged_issues,
    )

    get_runtime_store().latest_analysis = response.model_dump()
    return response
