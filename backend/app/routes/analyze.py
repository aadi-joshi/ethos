from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.models.analyze import AnalyzeRequestMetadata, AnalyzeResponse
from app.services.bias_service import (
    build_flagged_issues,
    calculate_demographic_parity_difference,
    calculate_disparate_impact_ratio,
    calculate_false_positive_rate_by_group,
    calculate_false_positive_rate_difference,
    calculate_selection_rate_by_group,
    load_dataframe_from_bytes,
    validate_required_columns,
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
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a valid CSV file.",
        )

    try:
        raw_bytes = await file.read()
        if not raw_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        dataframe = load_dataframe_from_bytes(raw_bytes)
        if dataframe.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset is empty.",
            )

        label_column = ground_truth_column or target_column
        validate_required_columns(
            dataframe,
            [target_column, sensitive_attribute, label_column],
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CSV input for analysis.",
        ) from error

    group_metrics = calculate_selection_rate_by_group(
        dataframe,
        target_column=target_column,
        sensitive_attribute=sensitive_attribute,
    )
    false_positive_rates = calculate_false_positive_rate_by_group(
        dataframe,
        prediction_column=target_column,
        label_column=ground_truth_column or target_column,
        sensitive_attribute=sensitive_attribute,
    )

    enriched_group_metrics = {
        group: {
            **metrics,
            "false_positive_rate": false_positive_rates.get(group, 0.0),
        }
        for group, metrics in group_metrics.items()
    }

    demographic_parity_difference = calculate_demographic_parity_difference(group_metrics)
    disparate_impact_ratio = calculate_disparate_impact_ratio(group_metrics)
    false_positive_rate_difference = calculate_false_positive_rate_difference(
        false_positive_rates
    )

    flagged_issues = build_flagged_issues(
        demographic_parity_difference=demographic_parity_difference,
        disparate_impact_ratio=disparate_impact_ratio,
        false_positive_rate_difference=false_positive_rate_difference,
    )

    response = AnalyzeResponse(
        request=AnalyzeRequestMetadata(
            target_column=target_column,
            sensitive_attribute=sensitive_attribute,
            ground_truth_column=ground_truth_column,
        ),
        group_metrics=enriched_group_metrics,
        overall_bias={
            "demographic_parity_difference": demographic_parity_difference,
            "disparate_impact_ratio": disparate_impact_ratio,
            "false_positive_rate_difference": false_positive_rate_difference,
        },
        flagged_issues=flagged_issues,
    )

    get_runtime_store().latest_analysis = response.model_dump()
    return response
