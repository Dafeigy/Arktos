"""ModerationDetector — detects harmful, illegal, and policy-violating content."""

import logging
from typing import Literal

from arktos.app.detectors.base import BaseDetector
from arktos.app.detectors.moderation.patterns import load_patterns, ModerationPatterns
from arktos.app.schemas.context import GuardContext
from arktos.app.schemas.detector import DetectorResult

logger = logging.getLogger(__name__)

# Map severity labels to numeric weight for risk scoring
SEVERITY_WEIGHT: dict[str, float] = {
    "critical": 1.0,
    "high": 0.8,
    "medium": 0.5,
    "low": 0.3,
}


class ModerationDetector(BaseDetector):
    """Checks input text against content moderation keyword lists.

    SignalDetector only — returns Blocked or Passed, never Masked.
    """

    name = "moderation"
    priority = 30
    timeout_ms = 50
    can_short_circuit = False
    detector_type = "signal"

    def __init__(self):
        self._patterns: ModerationPatterns = load_patterns()

    async def detect(self, context: GuardContext) -> DetectorResult:
        try:
            return self._run_detection(context.normalized_text)
        except Exception as exc:
            logger.exception("ModerationDetector failed for trace %s", context.trace_id)
            return self._error_result(str(exc))

    def _run_detection(self, text: str) -> DetectorResult:
        text_lower = text.lower()
        matches: list[dict] = []
        reason_codes: list[str] = []
        weighted_score: float = 0.0
        highest_severity: str = "low"

        for category_name, cat in self._patterns.categories.items():
            severity = cat["severity"]
            for keyword in cat["keywords"]:
                if keyword in text_lower:
                    matches.append({
                        "type": "moderation_keyword",
                        "category": category_name,
                        "severity": severity,
                        "pattern": keyword,
                    })
                    reason_codes.append(f"moderation.{category_name}")
                    weighted_score += SEVERITY_WEIGHT.get(severity, 0.3)

                    # Track highest severity
                    sev_order = ["low", "medium", "high", "critical"]
                    if sev_order.index(severity) > sev_order.index(highest_severity):
                        highest_severity = severity

        if not matches:
            return self._passed()

        # Decision logic
        if highest_severity == "critical" or weighted_score >= 1.5:
            risk_level: Literal["low", "medium", "high", "critical"] = "critical"
            should_block = True
        elif highest_severity == "high" or weighted_score >= 1.0:
            risk_level = "high"
            should_block = True
        elif weighted_score >= 0.5:
            risk_level = "medium"
            should_block = True
        else:
            risk_level = "low"
            should_block = False

        return DetectorResult(
            detector=self.name,
            status="Blocked" if should_block else "Passed",
            risk_level=risk_level,
            reason_codes=reason_codes,
            matches=matches,
            should_short_circuit=should_block and highest_severity == "critical",
            metadata={
                "detector_type": self.detector_type,
                "match_count": len(matches),
                "weighted_score": round(weighted_score, 2),
                "highest_severity": highest_severity,
            },
        )
