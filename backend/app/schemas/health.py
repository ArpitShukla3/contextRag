"""API response schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response payload for the health endpoint."""

    status: str