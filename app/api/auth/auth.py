from email.header import Header

from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.services.user_service import (
    get_user_token,
    get_refresh_token,
)
from app.config.config import get_db

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)


@auth_router.post("/token", status_code=status.HTTP_200_OK)
async def authenticate_user(
    data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return await get_user_token(data, db)


@auth_router.post("/refresh-token", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    refresh_token: str = Header(), db: Session = Depends(get_db)
):
    return await get_refresh_token(token=refresh_token, db=db)
