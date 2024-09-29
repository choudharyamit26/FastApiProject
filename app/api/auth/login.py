from email.header import Header

from fastapi import APIRouter, status, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.auth.schemas import CreateUserRequest, UserResponse
from app.api.models.models import User
from app.api.services.user_service import (
    create_user_account,
    get_user_token,
    get_refresh_token,
)
from app.config.config import get_db
from app.utils.security import oauth_scheme2, get_token_payload

router = APIRouter(
    prefix="/login", tags=["User"], responses={404: {"description": "Not found"}}
)


@router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(data: CreateUserRequest, db: Session = Depends(get_db)):
    await create_user_account(data, db)
    payload = {
        "message": "User created successfully",
        "status": status.HTTP_201_CREATED,
        "data": data.model_dump_json(),
    }
    return JSONResponse(content=payload)


@router.post("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_detail(
    request: Request,
    authenticated: str = Depends(oauth_scheme2),
    db: Session = Depends(get_db),
):
    # Get token payload
    payload = await get_token_payload(authenticated)
    if payload is None:
        return JSONResponse(
            content={"message": "Invalid or expired token"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Fetch user from the database
    user_id = payload.get("id")
    if user_id is None:
        return JSONResponse(
            content={"message": "Invalid token: no user id found"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return JSONResponse(
            content={"message": "User not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Return user details
    return request.user


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
