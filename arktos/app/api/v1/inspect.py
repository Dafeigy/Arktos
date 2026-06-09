"""POST /v1/inspect — the core detection endpoint."""

import logging

from fastapi import APIRouter

from arktos.app.audit.logger import log_inspect
from arktos.app.core.config import settings
from arktos.app.detectors.base import BaseDetector
from arktos.app.orchestrator.pipeline import run_pipeline
from arktos.app.policy.engine import decide
from arktos.app.schemas.context import GuardContext
from arktos.app.schemas.request import InspectRequest
from arktos.app.schemas.response import InspectResponse
from arktos.app.utils.text import normalize_text, truncate_text

logger = logging.getLogger(__name__)

router = APIRouter(tags=["inspect"])

# Detector registry — populated at app startup via register_detectors()
_detectors: list[BaseDetector] = []


def register_detectors(detectors: list[BaseDetector]) -> None:
    """Register the detector instances to use for inspection.

    Called once during app startup from main.py.
    """
    global _detectors
    _detectors = detectors
    names = [d.name for d in detectors]
    logger.info("Registered %d detectors: %s", len(detectors), names)


# Note: register_detectors is imported before the module is fully loaded.
# The actual registration happens in main.py after all imports resolve.


@router.post("/v1/inspect", response_model=InspectResponse)
async def inspect(request: InspectRequest):
    """Inspect input text for sensitive data, injection, and policy violations.

    Returns Passed, Masked, or Blocked with a full audit trail.
    """
    # ── Preprocessing ──
    text = truncate_text(request.text, settings.max_text_length)
    normalized, has_suspicious = normalize_text(text)

    # ── Build context ──
    context = GuardContext(
        original_text=request.text,
        normalized_text=normalized,
        app_id=request.app_id,
        tenant_id=request.tenant_id,
        environment=request.environment,
        user_id=request.user_id,
        session_id=request.session_id,
        metadata={
            "context": request.context or {},
            "has_suspicious_chars": has_suspicious,
        },
        policy_id=request.policy_id,
    )

    # ── Run pipeline ──
    results = await run_pipeline(context, _detectors)

    # ── Decide ──
    response = decide(context, results)

    # ── Audit (non-blocking) ──
    await log_inspect(context, response, results)

    return response
