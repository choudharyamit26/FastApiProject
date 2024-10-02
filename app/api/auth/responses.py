from typing import List

from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    product_name: str
    quantity: int

    class Config:
        from_attributes = True


class UserWithOrdersResponse(BaseModel):
    id: int
    name: str
    email: str
    orders: List[OrderResponse]

    class Config:
        from_attributes = True
