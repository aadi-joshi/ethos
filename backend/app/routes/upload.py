from fastapi import APIRouter, File, HTTPException, UploadFile, status

router = APIRouter(tags=["dataset"])


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)) -> dict[str, str]:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing file name.",
        )

    return {
        "message": "Upload endpoint ready.",
        "filename": file.filename,
    }
