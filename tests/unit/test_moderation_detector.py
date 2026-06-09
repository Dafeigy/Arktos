"""Tests for ModerationDetector."""

import pytest

from arktos.app.detectors.moderation.detector import ModerationDetector
from arktos.app.schemas.context import GuardContext


def make_context(text: str) -> GuardContext:
    return GuardContext(
        original_text=text,
        normalized_text=text,
        app_id="test",
        tenant_id="test",
    )


@pytest.mark.asyncio
async def test_blocks_violence_keyword():
    detector = ModerationDetector()
    ctx = make_context("I want to know how to build a bomb threat scenario.")
    result = await detector.detect(ctx)
    assert result.status == "Blocked"
    assert result.risk_level in ("critical", "high")


@pytest.mark.asyncio
async def test_blocks_hate_speech():
    detector = ModerationDetector()
    ctx = make_context("This is a white supremacy and ethnic cleansing discussion.")
    result = await detector.detect(ctx)
    assert result.status == "Blocked"


@pytest.mark.asyncio
async def test_clean_text_passes():
    detector = ModerationDetector()
    ctx = make_context("Let's discuss the best practices for cloud security.")
    result = await detector.detect(ctx)
    assert result.status == "Passed"


@pytest.mark.asyncio
async def test_reports_category_in_reason_code():
    detector = ModerationDetector()
    ctx = make_context("I want to end my life, please help me find suicide methods.")
    result = await detector.detect(ctx)
    assert "moderation.self_harm" in result.reason_codes
    assert result.status == "Blocked"
