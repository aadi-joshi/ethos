from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.services.bias_service import (
    calculate_selection_rate_by_group,
    load_dataframe_from_bytes,
    validate_required_columns,
)

router = APIRouter(tags=["analysis"])


@router.post("/analyze")
async def analyze_bias(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    sensitive_attribute: str = Form(...),
) -> dict:
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

        validate_required_columns(dataframe, target_column, sensitive_attribute)
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

    return {
        "group_metrics": group_metrics,
        "overall_bias": {},
        "flagged_issues": [],
    }
