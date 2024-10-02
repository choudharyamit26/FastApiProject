from typing import List

from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


# Request Model for creating an order with multiple products
class OrderProductRequest(BaseModel):
    product_id: int
    quantity: int


class CreateOrderRequest(BaseModel):
    user_id: int
    products: List[OrderProductRequest]
