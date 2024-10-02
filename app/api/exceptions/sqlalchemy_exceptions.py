import logging

from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from main import app

# Create a logger for capturing errors
logger = logging.getLogger(__name__)


# Global Exception Handler for SQLAlchemy Errors
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred.", "error": exc},
    )


# Global Exception Handler for Python's built-in exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )
