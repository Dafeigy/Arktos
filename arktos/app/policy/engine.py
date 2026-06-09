"""Policy decision engine — aggregates detector results into a final verdict."""

from typing import Literal

from arktos.app.policy.mask_merger import merge_mask_spans
from arktos.app.schemas.context import GuardContext
from arktos.app.schemas.detector import DetectorResult, MaskSpan
from arktos.app.schemas.response import InspectResponse


# Ordered risk levels for computing max
_RISK_ORDER: dict[str, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}


def _max_risk(*levels: str) -> Literal["low", "medium", "high", "critical"]:
    """Return the highest risk level from the given set."""
    max_val = max(_RISK_ORDER.get(level, 0) for level in levels)
    for label, val in _RISK_ORDER.items():
        if val == max_val:
            return label  # type: ignore[return-value]
    return "low"


def _collect_matched_rules(results: list[DetectorResult]) -> list[str]:
    """Collect unique rule names from all detector results."""
    rules: set[str] = set()
    for result in results:
        for reason in result.reason_codes:
            rules.add(reason)
    return sorted(rules)


def _collect_detectors(results: list[DetectorResult]) -> list[str]:
    """Collect unique detector names that had findings."""
    names: set[str] = set()
    for result in results:
        if result.status != "Passed":
            names.add(result.detector)
    return sorted(names)


def _collect_reason_codes(results: list[DetectorResult]) -> list[str]:
    """Collect all reason codes from detector results."""
    codes: list[str] = []
    for result in results:
        codes.extend(result.reason_codes)
    return codes


def decide(context: GuardContext, results: list[DetectorResult]) -> InspectResponse:
    """Aggregate detector results and produce the final InspectResponse.

    Decision rules (per architecture doc):
      - Any Blocked → final is Blocked.
      - Else, collect all MaskSpans → merge → if any accepted → Masked.
      - Otherwise → Passed.
    """
    # ── Blocked check ──
    blocked_results = [r for r in results if r.status == "Blocked"]
    if blocked_results:
        risk_level = _max_risk(*(r.risk_level for r in blocked_results))
        return InspectResponse(
            decision="Blocked",
            risk_level=risk_level,
            matched_rules=_collect_matched_rules(blocked_results),
            detectors=_collect_detectors(blocked_results),
            redacted_text=None,
            reason_codes=_collect_reason_codes(blocked_results),
            trace_id=context.trace_id,
            latency_ms=round(context.elapsed_ms, 2),
        )

    # ── Masked check ──
    all_spans: list[MaskSpan] = []
    for result in results:
        all_spans.extend(result.mask_spans)

    if all_spans:
        masked_text, accepted_spans = merge_mask_spans(context.normalized_text, all_spans)
        if accepted_spans:
            risk_level = _max_risk(*(r.risk_level for r in results))
            return InspectResponse(
                decision="Masked",
                risk_level=risk_level,
                matched_rules=_collect_matched_rules(results),
                detectors=_collect_detectors(results),
                redacted_text=masked_text,
                reason_codes=_collect_reason_codes(results),
                trace_id=context.trace_id,
                latency_ms=round(context.elapsed_ms, 2),
            )

    # ── Passed ──
    return InspectResponse(
        decision="Passed",
        risk_level="low",
        matched_rules=[],
        detectors=[],
        redacted_text=None,
        reason_codes=[],
        trace_id=context.trace_id,
        latency_ms=round(context.elapsed_ms, 2),
    )
