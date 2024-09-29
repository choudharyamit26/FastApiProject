import uvicorn
from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware

from app.api.auth.login import router as user_router, auth_router
from app.utils.security import JWTAuth

app = FastAPI()


app.add_middleware(AuthenticationMiddleware, backend=JWTAuth())
app.include_router(user_router)
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
