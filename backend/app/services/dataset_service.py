from __future__ import annotations

from io import StringIO

import pandas as pd
from fastapi import HTTPException, UploadFile, status

ALLOWED_CONTENT_TYPES = {
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "text/plain",
}


async def parse_csv_upload(file: UploadFile) -> tuple[list[str], dict, list[dict]]:
    _validate_csv_file(file)

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        decoded = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file encoding. Please upload a UTF-8 CSV file.",
        ) from error

    try:
        dataframe = pd.read_csv(StringIO(decoded))
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CSV format.",
        ) from error

    if dataframe.empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset is empty.",
        )

    if dataframe.isnull().values.any():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Dataset contains missing data. Please clean missing values and try again.",
        )

    columns = dataframe.columns.tolist()
    basic_stats = _build_basic_stats(dataframe)
    preview_rows = dataframe.head(5).to_dict(orient="records")

    return columns, basic_stats, preview_rows


def _validate_csv_file(file: UploadFile) -> None:
    filename = (file.filename or "").lower()

    if not filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only CSV files are supported.",
        )

    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid content type. Please upload a CSV file.",
        )


def _build_basic_stats(dataframe: pd.DataFrame) -> dict:
    numeric_summary: dict[str, dict[str, float]] = {}
    numeric_columns = dataframe.select_dtypes(include="number")

    if not numeric_columns.empty:
        describe_frame = numeric_columns.describe().transpose()
        numeric_summary = {
            column: {
                stat_name: _to_python_number(stat_value)
                for stat_name, stat_value in stats.items()
            }
            for column, stats in describe_frame.to_dict(orient="index").items()
        }

    missing_values = {
        column: int(count)
        for column, count in dataframe.isnull().sum().to_dict().items()
    }

    return {
        "row_count": int(len(dataframe)),
        "column_count": int(len(dataframe.columns)),
        "missing_values": missing_values,
        "dtypes": {column: str(dtype) for column, dtype in dataframe.dtypes.items()},
        "numeric_summary": numeric_summary,
    }


def _to_python_number(value: float) -> float:
    return float(value)
