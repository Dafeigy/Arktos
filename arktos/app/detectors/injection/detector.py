"""InjectionDetector — detects prompt injection and jailbreak attempts."""

import logging
from typing import Literal

from arktos.app.detectors.base import BaseDetector
from arktos.app.detectors.injection.patterns import load_patterns, InjectionPatterns
from arktos.app.schemas.context import GuardContext
from arktos.app.schemas.detector import DetectorResult

logger = logging.getLogger(__name__)


class InjectionDetector(BaseDetector):
    """Detects prompt injection and jailbreak patterns.

    Two-tier detection:
    - Pre-gate (priority 1): high-confidence keywords → immediate Blocked + short_circuit
    - Standard (priority 20): lower-confidence patterns → contribute to risk score

    Can be configured as a pre-gate or standard detector by switching `is_pre_gate`.
    """

    name = "injection"
    priority = 1  # Pre-gate: runs before most detectors
    timeout_ms = 50
    can_short_circuit = True
    detector_type = "signal"

    def __init__(self, is_pre_gate: bool = True):
        self.is_pre_gate = is_pre_gate
        self._patterns: InjectionPatterns = load_patterns()

    async def detect(self, context: GuardContext) -> DetectorResult:
        try:
            return self._run_detection(context.normalized_text)
        except Exception as exc:
            logger.exception("InjectionDetector failed for trace %s", context.trace_id)
            return self._error_result(str(exc))

    def _run_detection(self, text: str) -> DetectorResult:
        text_lower = text.lower()
        matches: list[dict] = []
        reason_codes: list[str] = []

        # ── Pre-gate pass: high-confidence patterns ──
        if self.is_pre_gate:
            for keyword in self._patterns.pre_gate_keywords:
                if keyword in text_lower:
                    matches.append({"type": "pre_gate_keyword", "pattern": keyword})
                    reason_codes.append("injection.pre_gate.keyword")

            for display, regex, confidence in self._patterns.pre_gate_regexes:
                if regex.search(text):
                    matches.append({"type": "pre_gate_regex", "pattern": display})
                    reason_codes.append("injection.pre_gate.regex")

            if matches:
                return DetectorResult(
                    detector=self.name,
                    status="Blocked",
                    risk_level="critical",
                    reason_codes=reason_codes,
                    matches=matches,
                    should_short_circuit=True,
                    metadata={
                        "detector_type": self.detector_type,
                        "match_count": len(matches),
                        "tier": "pre_gate",
                    },
                )
            return self._passed()

        # ── Standard pass: lower-confidence patterns ──
        for keyword in self._patterns.standard_keywords:
            if keyword in text_lower:
                matches.append({"type": "standard_keyword", "pattern": keyword})
                reason_codes.append("injection.standard.keyword")

        for display, regex, confidence in self._patterns.standard_regexes:
            if regex.search(text):
                matches.append({"type": "standard_regex", "pattern": display})
                reason_codes.append("injection.standard.regex")

        if not matches:
            return self._passed()

        # Risk scoring
        match_count = len(matches)
        if match_count >= 3:
            risk_level: Literal["low", "medium", "high", "critical"] = "critical"
            should_block = True
        elif match_count >= 2:
            risk_level = "high"
            should_block = True
        else:
            risk_level = "medium"
            should_block = False

        return DetectorResult(
            detector=self.name,
            status="Blocked" if should_block else "Passed",
            risk_level=risk_level,
            reason_codes=reason_codes,
            matches=matches,
            should_short_circuit=should_block,
            metadata={
                "detector_type": self.detector_type,
                "match_count": match_count,
                "tier": "standard",
            },
        )
