"""Async audit logger — writes structured JSON events without blocking.

Design: uses an asyncio.Queue + background writer task.
Logs NEVER contain raw text — only hashed user IDs, summaries, and metadata.
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

from arktos.app.schemas.context import GuardContext
from arktos.app.schemas.detector import DetectorResult
from arktos.app.schemas.response import InspectResponse

logger = logging.getLogger(__name__)

# Internal queue for non-blocking audit writes
_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
_writer_task: asyncio.Task | None = None


def _hash(value: str | None) -> str | None:
    """SHA256-hash a value for safe audit storage."""
    if value is None:
        return None
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def _summarize_results(results: list[DetectorResult]) -> list[dict[str, Any]]:
    """Create a summary of detector results safe for audit logs."""
    summary = []
    for r in results:
        summary.append({
            "detector": r.detector,
            "status": r.status,
            "risk_level": r.risk_level,
            "reason_codes": r.reason_codes,
            "match_count": len(r.matches),
            "mask_span_count": len(r.mask_spans),
            "short_circuited": r.should_short_circuit,
            "skipped": r.metadata.get("skipped", False),
        })
    return summary


async def _audit_writer():
    """Background task that drains the audit queue and writes JSON lines to stdout."""
    while True:
        try:
            event = await _queue.get()
            # Write as a single JSON line to stdout — redirect to file/agent in production
            print(json.dumps(event, ensure_ascii=False), flush=True)
            _queue.task_done()
        except asyncio.CancelledError:
            # Drain remaining before exit
            while not _queue.empty():
                event = _queue.get_nowait()
                print(json.dumps(event, ensure_ascii=False), flush=True)
                _queue.task_done()
            return
        except Exception:
            logger.exception("Audit writer error")


async def start_audit_writer():
    """Start the background audit writer. Call during app startup."""
    global _writer_task
    if _writer_task is None or _writer_task.done():
        _writer_task = asyncio.create_task(_audit_writer())
        logger.info("Audit writer started")


async def stop_audit_writer():
    """Stop the background audit writer. Call during app shutdown."""
    global _writer_task
    if _writer_task and not _writer_task.done():
        _writer_task.cancel()
        try:
            await _writer_task
        except asyncio.CancelledError:
            pass
        _writer_task = None
        logger.info("Audit writer stopped")


async def log_inspect(
    context: GuardContext,
    response: InspectResponse,
    results: list[DetectorResult],
):
    """Enqueue an audit event for the inspect request. Non-blocking."""
    event = {
        "event": "inspect",
        "trace_id": context.trace_id,
        "tenant_id": context.tenant_id,
        "app_id": context.app_id,
        "user_id_hash": _hash(context.user_id),
        "policy_id": context.policy_id,
        "final_status": response.decision,
        "risk_level": response.risk_level,
        "reason_codes": response.reason_codes,
        "matched_rules": response.matched_rules,
        "detector_results": _summarize_results(results),
        "latency_ms": response.latency_ms,
        "short_circuited": any(r.metadata.get("skipped") for r in results),
        "text_length": len(context.original_text),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await _queue.put(event)
