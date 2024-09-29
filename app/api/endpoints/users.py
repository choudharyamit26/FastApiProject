from fastapi import APIRouter, status, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.auth.responses import UserResponse
from app.api.auth.schemas import CreateUserRequest
from app.api.services.user_service import (
    create_user_account,
)
from app.config.config import get_db
from app.utils.security import oauth_scheme2, get_token_payload

users_router = APIRouter(
    prefix="/users", tags=["User"], responses={404: {"description": "Not found"}}
)


@users_router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(data: CreateUserRequest, db: Session = Depends(get_db)):
    await create_user_account(data, db)
    payload = {
        "message": "User created successfully",
        "status": status.HTTP_201_CREATED,
        "data": data.model_dump_json(),
    }
    return JSONResponse(content=payload)


@users_router.post("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_detail(
    request: Request,
    authenticated: str = Depends(oauth_scheme2),
):
    # Get token payload
    payload = await get_token_payload(authenticated)
    if payload is None:
        return JSONResponse(
            content={"message": "Invalid or expired token"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Fetch user from the database
    # user_id = payload.get("id")
    # if user_id is None:
    #     return JSONResponse(
    #         content={"message": "Invalid token: no user id found"},
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #     )
    #
    # user = db.query(User).filter(User.id == user_id).first()
    # if user is None:
    #     return JSONResponse(
    #         content={"message": "User not found"},
    #         status_code=status.HTTP_404_NOT_FOUND,
    #     )

    # Return user details
    return request.user
