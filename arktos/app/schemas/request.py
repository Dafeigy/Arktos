"""Inspect API request models."""

from typing import Any

from pydantic import BaseModel, Field


class InspectRequest(BaseModel):
    """Request body for POST /v1/inspect."""

    app_id: str = Field(..., min_length=1, max_length=128, description="Application identifier")
    tenant_id: str = Field(..., min_length=1, max_length=128, description="Tenant identifier")
    environment: str = Field(default="production", max_length=64)
    user_id: str | None = Field(default=None, max_length=256)
    session_id: str | None = Field(default=None, max_length=256)
    text: str = Field(..., min_length=1, max_length=32768, description="Input text to inspect")
    context: dict[str, Any] | None = Field(default=None, description="Optional history or metadata")
    policy_id: str | None = Field(default=None, max_length=128)
