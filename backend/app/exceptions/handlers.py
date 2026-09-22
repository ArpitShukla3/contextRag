"""Exception handler registration."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.exceptions.errors import AppError

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register JSON exception handlers on the FastAPI application."""

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        logger.error("Application error: %s", exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."},
        )