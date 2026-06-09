"""Tests for the pipeline orchestrator."""

import asyncio

import pytest

from arktos.app.detectors.base import BaseDetector
from arktos.app.orchestrator.pipeline import run_pipeline
from arktos.app.schemas.context import GuardContext
from arktos.app.schemas.detector import DetectorResult


class _FakeBlockingDetector(BaseDetector):
    name = "fake_blocker"
    priority = 1
    can_short_circuit = True
    detector_type = "signal"

    async def detect(self, context: GuardContext) -> DetectorResult:
        return DetectorResult(
            detector=self.name,
            status="Blocked",
            risk_level="critical",
            reason_codes=["fake.block"],
            should_short_circuit=True,
        )


class _FakePassingDetector(BaseDetector):
    name = "fake_passer"
    priority = 50
    detector_type = "signal"

    async def detect(self, context: GuardContext) -> DetectorResult:
        return DetectorResult(
            detector=self.name,
            status="Passed",
            risk_level="low",
        )


class _SlowDetector(BaseDetector):
    name = "fake_slow"
    priority = 50
    timeout_ms = 5000
    detector_type = "signal"

    async def detect(self, context: GuardContext) -> DetectorResult:
        await asyncio.sleep(10)  # Will be cancelled
        return DetectorResult(detector=self.name, status="Passed", risk_level="low")


class _TransformDetector(BaseDetector):
    name = "fake_transform"
    priority = 20
    detector_type = "transform"

    async def detect(self, context: GuardContext) -> DetectorResult:
        from arktos.app.schemas.detector import MaskSpan
        span = MaskSpan(start=0, end=5, replacement="[REDACTED]", mask_type="pii", detector=self.name)
        return DetectorResult(
            detector=self.name,
            status="Masked",
            mask_spans=[span],
            reason_codes=["fake.mask"],
        )


@pytest.mark.asyncio
async def test_pre_gate_short_circuits():
    ctx = GuardContext(
        original_text="test", normalized_text="test",
        app_id="app", tenant_id="t",
    )
    detectors = [_FakeBlockingDetector(), _FakePassingDetector()]
    results = await run_pipeline(ctx, detectors)

    statuses = {r.detector: r.status for r in results}
    assert statuses.get("fake_blocker") == "Blocked"
    # The passer should be marked as skipped
    passer = next(r for r in results if r.detector == "fake_passer")
    assert passer.metadata.get("skipped") is True


@pytest.mark.asyncio
async def test_all_pass_returns_results():
    ctx = GuardContext(
        original_text="test", normalized_text="test",
        app_id="app", tenant_id="t",
    )
    detectors = [_FakePassingDetector(), _FakePassingDetector()]
    results = await run_pipeline(ctx, detectors)
    assert len(results) == 2
    assert all(r.status == "Passed" for r in results)


@pytest.mark.asyncio
async def test_transform_detector_returns_spans():
    ctx = GuardContext(
        original_text="hello", normalized_text="hello",
        app_id="app", tenant_id="t",
    )
    detectors = [_TransformDetector()]
    results = await run_pipeline(ctx, detectors)
    assert len(results) == 1
    assert results[0].status == "Masked"
    assert len(results[0].mask_spans) == 1
