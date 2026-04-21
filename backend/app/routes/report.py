from fastapi import APIRouter

from app.models.report import ReportResponse
from app.services.report_service import generate_report

router = APIRouter(tags=["report"])


@router.get("/report", response_model=ReportResponse)
def get_report() -> ReportResponse:
    return generate_report()
