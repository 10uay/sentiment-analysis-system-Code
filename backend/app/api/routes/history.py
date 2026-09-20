from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.schemas import HistoryItem
from app.dependencies import get_current_user, get_db
from app.db import crud

router = APIRouter()


@router.get("/history", response_model=list[HistoryItem])
def get_history(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
):
    return crud.get_history(db=db, user_id=user, limit=limit, offset=offset)
