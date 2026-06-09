"""Abstract base class for all detectors."""

from abc import ABC, abstractmethod
from typing import Literal

from arktos.app.schemas.context import GuardContext
from arktos.app.schemas.detector import DetectorResult


class BaseDetector(ABC):
    """Every detector inherits from this and implements detect().

    Class attributes configure behaviour; the orchestrator reads them directly.
    """

    # ── Set by subclasses ──
    name: str = "base"
    priority: int = 100  # Lower = higher priority, runs earlier
    timeout_ms: int = 100
    enabled: bool = True
    can_short_circuit: bool = False
    detector_type: Literal["signal", "transform"] = "signal"

    # ── Public API ──

    @abstractmethod
    async def detect(self, context: GuardContext) -> DetectorResult:
        """Run detection on `context.normalized_text`.

        Subclasses MUST return a DetectorResult. They SHOULD handle exceptions
        internally and return a Passed result with error metadata on failure.
        """

    # ── Helpers ──

    def _passed(self) -> DetectorResult:
        return DetectorResult(
            detector=self.name,
            status="Passed",
            risk_level="low",
            metadata={"detector_type": self.detector_type},
        )

    def _blocked(
        self,
        reason_codes: list[str],
        risk_level: Literal["low", "medium", "high", "critical"] = "high",
        matches: list[dict] | None = None,
        short_circuit: bool = False,
    ) -> DetectorResult:
        return DetectorResult(
            detector=self.name,
            status="Blocked",
            risk_level=risk_level,
            reason_codes=reason_codes,
            matches=matches or [],
            should_short_circuit=short_circuit and self.can_short_circuit,
            metadata={"detector_type": self.detector_type},
        )

    def _masked(
        self,
        mask_spans: list,
        reason_codes: list[str],
        risk_level: Literal["low", "medium", "high", "critical"] = "medium",
    ) -> DetectorResult:
        return DetectorResult(
            detector=self.name,
            status="Masked",
            risk_level=risk_level,
            reason_codes=reason_codes,
            mask_spans=mask_spans,
            metadata={"detector_type": self.detector_type},
        )

    def _error_result(self, error: str) -> DetectorResult:
        return DetectorResult(
            detector=self.name,
            status="Passed",  # Fail-open: let the request through on detector error
            risk_level="low",
            reason_codes=[f"{self.name}.error"],
            metadata={"detector_type": self.detector_type, "error": error},
        )
