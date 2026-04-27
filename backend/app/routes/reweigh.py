from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.services.bias_service import load_dataframe_from_bytes
from app.services.reweighing_service import apply_reweighing, dataframe_to_csv_bytes

router = APIRouter(tags=["mitigation"])


@router.post("/mitigate/reweigh")
async def reweigh_dataset(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    sensitive_attribute: str = Form(...),
) -> dict:
    """
    Apply Kamiran & Calders (2012) reweighing to the uploaded dataset.
    Returns summary of weight assignments. Use /mitigate/reweigh/download
    to get the corrected CSV.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a valid CSV file.")
    try:
        raw = await file.read()
        df = load_dataframe_from_bytes(raw)
        _, summary = apply_reweighing(df, target_column, sensitive_attribute)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mitigate/reweigh/download")
async def download_reweighed(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    sensitive_attribute: str = Form(...),
) -> Response:
    """Return the reweighed CSV with a new 'sample_weight' column for download."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a valid CSV file.")
    try:
        raw = await file.read()
        df = load_dataframe_from_bytes(raw)
        reweighed_df, _ = apply_reweighing(df, target_column, sensitive_attribute)
        csv_bytes = dataframe_to_csv_bytes(reweighed_df)
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=reweighed_dataset.csv"},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
