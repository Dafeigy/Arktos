"""SensitiveInfoDetector — detects PII, secrets, and internal assets via regex."""

import logging
from typing import Literal

from arktos.app.detectors.base import BaseDetector
from arktos.app.detectors.sensitive.patterns import CompiledPattern, load_patterns
from arktos.app.schemas.context import GuardContext
from arktos.app.schemas.detector import DetectorResult, MaskSpan

logger = logging.getLogger(__name__)

# Mask type → priority rank for conflict resolution (lower wins)
MASK_TYPE_RANK: dict[str, int] = {
    "secret": 0,
    "pii": 1,
    "internal_asset": 2,
    "keyword": 3,
}

# Risk level for a mask type if no explicit Blocked signal
MASK_TYPE_RISK: dict[str, Literal["low", "medium", "high", "critical"]] = {
    "secret": "critical",
    "pii": "medium",
    "internal_asset": "medium",
    "keyword": "low",
}


class SensitiveInfoDetector(BaseDetector):
    """Detects PII, secrets, and internal assets using compiled regex patterns.

    This is a TransformDetector: it produces MaskSpan suggestions but can also
    return Blocked for high-severity secrets (private keys, hardcoded tokens).
    """

    name = "sensitive_info"
    priority = 10
    timeout_ms = 80
    can_short_circuit = False
    detector_type = "transform"

    def __init__(self):
        self._patterns: list[CompiledPattern] = load_patterns()

    async def detect(self, context: GuardContext) -> DetectorResult:
        try:
            return self._run_detection(context.normalized_text)
        except Exception as exc:
            logger.exception("SensitiveInfoDetector failed for trace %s", context.trace_id)
            return self._error_result(str(exc))

    def _run_detection(self, text: str) -> DetectorResult:
        all_spans: list[MaskSpan] = []
        all_reason_codes: list[str] = []
        has_secret: bool = False

        for pattern in self._patterns:
            for match in pattern.regex.finditer(text):
                span = MaskSpan(
                    start=match.start(),
                    end=match.end(),
                    replacement=pattern.replacement,
                    mask_type=pattern.mask_type,  # type: ignore[arg-type]
                    priority=pattern.priority,
                    confidence=pattern.confidence,
                    detector=self.name,
                    reason_code=f"sensitive.{pattern.name}",
                )
                all_spans.append(span)
                all_reason_codes.append(f"sensitive.{pattern.name}")

                if pattern.mask_type == "secret":
                    has_secret = True

        if not all_spans:
            return self._passed()

        # Secrets → Blocked (private keys, hardcoded tokens are too risky to just mask)
        if has_secret:
            return DetectorResult(
                detector=self.name,
                status="Blocked",
                risk_level="critical",
                reason_codes=all_reason_codes,
                mask_spans=all_spans,
                matches=[{"type": s.mask_type, "reason": s.reason_code} for s in all_spans],
                metadata={"detector_type": self.detector_type, "span_count": len(all_spans)},
            )

        # PII / internal assets → Masked
        return DetectorResult(
            detector=self.name,
            status="Masked",
            risk_level="medium",
            reason_codes=all_reason_codes,
            mask_spans=all_spans,
            matches=[{"type": s.mask_type, "reason": s.reason_code} for s in all_spans],
            metadata={"detector_type": self.detector_type, "span_count": len(all_spans)},
        )
