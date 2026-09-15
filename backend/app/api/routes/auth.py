from fastapi import APIRouter

from app.api.schemas import LoginRequest, TokenResponse
from app.dependencies import create_access_token

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    # نسخة تعليمية مبسطة. في الإنتاج يجب استخدام جدول مستخدمين وكلمات مرور مشفرة.
    token = create_access_token(subject=payload.username)
    return TokenResponse(access_token=token)
