import logging
from datetime import timedelta, datetime

import jwt
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette.authentication import (
    AuthCredentials,
    UnauthenticatedUser,
    AuthenticationBackend,
)

from app.api.models.models import User
from app.api.services.user_service import get_settings
from app.config.config import get_db

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_scheme2 = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_password_hash(password_string):
    return pwd_context.hash(password_string)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def create_access_token(data, expire: timedelta):
    payload = data.copy()
    expire_time = datetime.now() + expire
    payload.update({"exp": expire_time})
    token = jwt.encode(
        payload=payload, key=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return token


async def create_refresh_token(data):
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def get_token_payload(token):
    try:
        payload = jwt.decode(
            jwt=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError as e:
        logging.info(f"Exception occurred at jwt decode:{e}")
        return None
    return payload


async def get_current_user(token: str = Depends(oauth_scheme2), db=None):
    payload = await get_token_payload(token)
    if not payload or type(payload) is not dict:
        return None
    user_id = payload.get("id", None)
    if not user_id:
        return None
    if not db:
        db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    # print("-------", [{key: value} for key, value in user])
    return user


class JWTAuth(AuthenticationBackend):
    async def authenticate(self, conn):
        guest = AuthCredentials(["unauthenticated"]), UnauthenticatedUser()
        if "authorization" not in conn.headers:
            return guest
        token = conn.headers.get("authorization").split(" ")[1]
        if not token:
            return guest
        user = await get_current_user(token=token)
        if not user:
            return guest
        return AuthCredentials("authenticated"), user
