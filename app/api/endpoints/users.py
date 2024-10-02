from fastapi import APIRouter, status, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.auth.responses import UserResponse, UserWithOrdersResponse
from app.api.auth.schemas import CreateUserRequest
from app.api.models.models import User, Order
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


# Sample endpoint for taking arbitrary number of query params
@users_router.get("/queries")
async def get_queries_from_path(request: Request):
    return JSONResponse(
        content=dict(request.query_params), status_code=status.HTTP_200_OK
    )


# Sample endpoint for taking path params and arbitrary number of query params
@users_router.get("/path-params/{name}/{age}")
async def get_queries_from_path(request: Request, name: str, age: int):
    query_params = dict(request.query_params)
    return JSONResponse(
        content={"name": name, "age": age, "query_params": query_params},
        status_code=status.HTTP_200_OK,
    )


# Endpoint to fetch user with their orders using a JOIN
@users_router.get("/users-with-orders/{user_id}", response_model=UserWithOrdersResponse)
def get_user_with_orders(user_id: int, db: Session = Depends(get_db)):
    # Perform a JOIN to get the user and their orders
    stmt = db.query(User).join(Order).filter(User.id == user_id).all()

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
