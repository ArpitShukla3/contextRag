"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.api import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()