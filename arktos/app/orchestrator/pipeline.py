"""Pipeline orchestrator — runs detectors in staged async execution.

Stage model:
  1. pre_gate  — high-priority detectors that can short-circuit
  2. parallel  — all remaining detectors run concurrently
  3. (post is handled by the policy engine, not the orchestrator)
"""

import asyncio
import logging

from arktos.app.core.config import settings
from arktos.app.detectors.base import BaseDetector
from arktos.app.schemas.context import GuardContext
from arktos.app.schemas.detector import DetectorResult

logger = logging.getLogger(__name__)


async def _run_detector(detector: BaseDetector, context: GuardContext) -> DetectorResult:
    """Run a single detector with timeout and error handling."""
    try:
        return await asyncio.wait_for(
            detector.detect(context),
            timeout=detector.timeout_ms / 1000.0,
        )
    except asyncio.TimeoutError:
        logger.warning("Detector '%s' timed out after %dms (trace=%s)",
                       detector.name, detector.timeout_ms, context.trace_id)
        return DetectorResult(
            detector=detector.name,
            status="Passed",  # Fail-open on timeout
            risk_level="low",
            reason_codes=[f"{detector.name}.timeout"],
            metadata={"detector_type": detector.detector_type, "error": "timeout"},
        )
    except Exception as exc:
        logger.exception("Detector '%s' crashed (trace=%s)", detector.name, context.trace_id)
        return DetectorResult(
            detector=detector.name,
            status="Passed",  # Fail-open
            risk_level="low",
            reason_codes=[f"{detector.name}.error"],
            metadata={"detector_type": detector.detector_type, "error": str(exc)},
        )


async def run_pipeline(
    context: GuardContext,
    detectors: list[BaseDetector],
) -> list[DetectorResult]:
    """Execute all enabled detectors in staged fashion.

    Returns a list of DetectorResult — one per detector that was invoked.
    The caller is responsible for feeding results to the policy engine.
    """
    enabled = [d for d in detectors if d.enabled]

    if not enabled:
        return []

    results: list[DetectorResult] = []

    # ── Stage 1: Pre-gate ──
    # Detectors with can_short_circuit=True run serially first.
    # If any returns Blocked + should_short_circuit, we bail immediately.
    pre_gate = [d for d in enabled if d.can_short_circuit]
    parallel_detectors = [d for d in enabled if not d.can_short_circuit]

    for detector in pre_gate:
        result = await _run_detector(detector, context)
        results.append(result)

        if result.should_short_circuit and result.status == "Blocked":
            logger.info(
                "Pre-gate detector '%s' short-circuited pipeline (trace=%s)",
                detector.name, context.trace_id,
            )
            # Run remaining pre-gate detectors? No — short-circuit means stop.
            # But we should mark the skipped detectors in results for audit.
            remaining = [d for d in pre_gate if d.name != detector.name]
            remaining += parallel_detectors
            for skipped in remaining:
                results.append(DetectorResult(
                    detector=skipped.name,
                    status="Passed",
                    risk_level="low",
                    reason_codes=[f"{skipped.name}.skipped"],
                    metadata={"detector_type": skipped.detector_type, "skipped": True},
                ))
            return results

    # ── Stage 2: Parallel ──
    if parallel_detectors:
        tasks = {
            asyncio.create_task(_run_detector(d, context)): d
            for d in parallel_detectors
        }

        try:
            # Wait for first to complete, then check for short-circuit
            pending = set(tasks.keys())
            while pending:
                done, pending = await asyncio.wait(
                    pending,
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in done:
                    detector = tasks.pop(task)
                    result = await task
                    results.append(result)

                    if result.should_short_circuit and result.status == "Blocked":
                        logger.info(
                            "Parallel detector '%s' triggered short-circuit (trace=%s)",
                            detector.name, context.trace_id,
                        )
                        # Cancel remaining tasks
                        for pending_task in pending:
                            pending_task.cancel()
                        # Wait for cancellations to propagate
                        await asyncio.gather(*pending, return_exceptions=True)
                        # Mark skipped detectors
                        for pending_task, skipped in zip(pending, [tasks[t] for t in pending]):
                            results.append(DetectorResult(
                                detector=skipped.name,
                                status="Passed",
                                risk_level="low",
                                reason_codes=[f"{skipped.name}.skipped"],
                                metadata={"detector_type": skipped.detector_type, "skipped": True},
                            ))
                        return results

        except asyncio.CancelledError:
            # Outer request was cancelled
            for task in tasks:
                if not task.done():
                    task.cancel()
            raise

    return results
