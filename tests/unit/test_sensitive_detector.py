"""Tests for SensitiveInfoDetector."""

import pytest

from arktos.app.detectors.sensitive.detector import SensitiveInfoDetector
from arktos.app.schemas.context import GuardContext


def make_context(text: str) -> GuardContext:
    return GuardContext(
        original_text=text,
        normalized_text=text,
        app_id="test",
        tenant_id="test",
    )


@pytest.mark.asyncio
async def test_detects_api_key():
    detector = SensitiveInfoDetector()
    ctx = make_context("My API key is sk-abc123def456ghi789jkl012mnop345qr")
    result = await detector.detect(ctx)
    assert result.status == "Blocked"
    assert "sensitive.openai_key" in result.reason_codes


@pytest.mark.asyncio
async def test_detects_email():
    detector = SensitiveInfoDetector()
    ctx = make_context("Contact me at alice@example.com for more info.")
    result = await detector.detect(ctx)
    assert result.status == "Masked"
    assert any("sensitive.email_address" in rc for rc in result.reason_codes)


@pytest.mark.asyncio
async def test_detects_phone_cn():
    detector = SensitiveInfoDetector()
    ctx = make_context("My phone is 13812345678, call me.")
    result = await detector.detect(ctx)
    assert result.status == "Masked"
    assert any("sensitive.phone_cn" in rc for rc in result.reason_codes)


@pytest.mark.asyncio
async def test_clean_text_passes():
    detector = SensitiveInfoDetector()
    ctx = make_context("Hello, how do I reset my password via the settings page?")
    result = await detector.detect(ctx)
    assert result.status == "Passed"


@pytest.mark.asyncio
async def test_produces_mask_spans():
    detector = SensitiveInfoDetector()
    ctx = make_context("Email: alice@example.com, Phone: 13812345678")
    result = await detector.detect(ctx)
    assert len(result.mask_spans) >= 2
    # Verify spans have valid offsets
    for span in result.mask_spans:
        assert span.start >= 0
        assert span.end > span.start
        assert span.replacement
