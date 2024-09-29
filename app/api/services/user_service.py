from datetime import datetime, timedelta

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from app.config.config import get_settings
from ..auth.responses import TokenResponse
from ..auth.schemas import CreateUserRequest
from ..models.models import User
from ...utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_token_payload,
)

settings = get_settings()


async def create_user_account(data: CreateUserRequest, db: Session):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already exists",
        )

    new_user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password=get_password_hash(data.password),
        is_active=False,
        is_verified=False,
        registered_at=datetime.now(),
        updated_at=datetime.now(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def get_user_token(data, db):
    user = db.query(User).filter(User.email == data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid login credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await _get_token(user=user)


async def get_refresh_token(token, db):
    payload = await get_token_payload(token)
    user_id = payload.get("id", None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await _get_token(user=user, refresh_token=token)


async def _get_token(user: User, refresh_token=None):
    payload = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
    access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(payload, access_token_expire)
    if not refresh_token:
        refresh_token = await create_refresh_token(payload)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_token_expire.seconds,
    )
