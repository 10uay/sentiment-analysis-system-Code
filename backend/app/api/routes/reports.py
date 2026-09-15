from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.schemas import ReportRequest
from app.dependencies import get_current_user, get_db
from app.db import crud
from app.services.report_service import ReportService

router = APIRouter()
report_service = ReportService()


@router.post("/report")
def create_report(
    payload: ReportRequest,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
):
    rows = crud.get_analyses_by_ids(db=db, user_id=user, ids=payload.analysis_ids)
    if payload.export_format == "csv":
        content = report_service.generate_csv(rows)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=sentiment_report.csv"},
        )

    if payload.export_format == "json":
        return {"items": [crud.analysis_to_dict(x) for x in rows]}

    pdf = report_service.generate_pdf(rows, include_charts=payload.include_charts)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sentiment_report.pdf"},
    )
