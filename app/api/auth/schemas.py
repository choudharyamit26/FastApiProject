from datetime import datetime

from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
