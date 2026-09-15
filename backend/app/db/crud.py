from typing import Iterable
from sqlalchemy.orm import Session

from app.db.models import Analysis


def create_analysis(
    db: Session,
    user_id: str,
    text: str,
    cleaned_text: str,
    language: str,
    label: str,
    confidence: float,
    model_name: str,
    raw_result: dict,
) -> Analysis:
    item = Analysis(
        user_id=user_id,
        text=text,
        cleaned_text=cleaned_text,
        language=language,
        label=label,
        confidence=confidence,
        model_name=model_name,
        raw_result=raw_result,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_history(db: Session, user_id: str, limit: int = 50, offset: int = 0) -> list[Analysis]:
    query = db.query(Analysis)
    if user_id != "anonymous":
        query = query.filter(Analysis.user_id == user_id)
    return query.order_by(Analysis.created_at.desc()).offset(offset).limit(limit).all()


def get_analyses_by_ids(db: Session, user_id: str, ids: Iterable[int]) -> list[Analysis]:
    query = db.query(Analysis)
    ids = list(ids)
    if ids:
        query = query.filter(Analysis.id.in_(ids))
    if user_id != "anonymous":
        query = query.filter(Analysis.user_id == user_id)
    return query.order_by(Analysis.created_at.desc()).all()


def analysis_to_dict(item: Analysis) -> dict:
    return {
        "id": item.id,
        "text": item.text,
        "cleaned_text": item.cleaned_text,
        "language": item.language,
        "label": item.label,
        "confidence": item.confidence,
        "model_name": item.model_name,
        "raw_result": item.raw_result,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }
