from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.models.dataset import UploadResponse
from app.services.dataset_service import parse_csv_upload

router = APIRouter(tags=["dataset"])


@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing file name.",
        )

    columns, basic_stats, preview_rows = await parse_csv_upload(file)

    return UploadResponse(
        columns=columns,
        basic_stats=basic_stats,
        preview_rows=preview_rows,
    )
