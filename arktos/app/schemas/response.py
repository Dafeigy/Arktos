"""Inspect API response models."""

from typing import Literal

from pydantic import BaseModel, Field


class InspectResponse(BaseModel):
    """Response body for POST /v1/inspect."""

    decision: Literal["Passed", "Masked", "Blocked"]
    risk_level: Literal["low", "medium", "high", "critical"]
    matched_rules: list[str] = Field(default_factory=list)
    detectors: list[str] = Field(default_factory=list)
    redacted_text: str | None = Field(default=None)
    reason_codes: list[str] = Field(default_factory=list)
    trace_id: str
    latency_ms: float
