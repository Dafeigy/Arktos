"""Detector result models — shared between detectors and policy engine."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class MaskSpan(BaseModel):
    """A suggested text span to redact, produced by a TransformDetector."""

    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)
    replacement: str
    mask_type: Literal["secret", "pii", "internal_asset", "keyword"] = "pii"
    priority: int = Field(default=10)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    detector: str = ""
    reason_code: str = ""


class DetectorCapabilities(BaseModel):
    """Declares what a detector can produce."""

    can_block: bool = True
    can_mask: bool = False
    can_pass: bool = True


class DetectorResult(BaseModel):
    """Uniform result from any detector — signals only, no final decision."""

    detector: str
    status: Literal["Blocked", "Masked", "Passed"]
    risk_level: Literal["low", "medium", "high", "critical"] = "low"
    reason_codes: list[str] = Field(default_factory=list)
    matches: list[dict[str, Any]] = Field(default_factory=list)
    mask_spans: list[MaskSpan] = Field(default_factory=list)
    should_short_circuit: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
