from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Generator

from fastapi import Depends, Header, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.database import SessionLocal

settings = get_settings()

_request_counter: dict[str, list[datetime]] = defaultdict(list)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def get_current_user(authorization: str | None = Header(default=None)) -> str:
    if not authorization:
        return "anonymous"

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload.get("sub", "anonymous")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def rate_limit(request: Request, limit: int = 120, window_seconds: int = 60):
    client = request.client.host if request.client else "unknown"
    now = datetime.now(timezone.utc)
    bucket = _request_counter[client]
    _request_counter[client] = [t for t in bucket if (now - t).total_seconds() < window_seconds]
    if len(_request_counter[client]) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    _request_counter[client].append(now)
    return True
