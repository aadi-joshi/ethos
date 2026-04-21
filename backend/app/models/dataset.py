from typing import Any

from pydantic import BaseModel


class UploadResponse(BaseModel):
    columns: list[str]
    basic_stats: dict[str, Any]
    preview_rows: list[dict[str, Any]]
