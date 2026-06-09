"""Tests for mask span merging."""

from arktos.app.policy.mask_merger import merge_mask_spans
from arktos.app.schemas.detector import MaskSpan


def test_no_spans_returns_original():
    text = "Hello, world!"
    result, spans = merge_mask_spans(text, [])
    assert result == text
    assert spans == []


def test_single_span():
    text = "My email is alice@example.com"
    # "alice@example.com" starts at index 12, ends at index 29
    span = MaskSpan(
        start=12,
        end=29,
        replacement="[REDACTED_EMAIL]",
        mask_type="pii",
        detector="sensitive_info",
    )
    result, accepted = merge_mask_spans(text, [span])
    assert result == "My email is [REDACTED_EMAIL]"
    assert len(accepted) == 1


def test_non_overlapping_spans():
    text = "Email: alice@example.com, Phone: 13812345678"
    # "alice@example.com" = 7..24, "13812345678" = 33..44
    spans = [
        MaskSpan(start=7, end=24, replacement="[EMAIL]", mask_type="pii", detector="sensitive_info"),
        MaskSpan(start=33, end=44, replacement="[PHONE]", mask_type="pii", detector="sensitive_info"),
    ]
    result, accepted = merge_mask_spans(text, spans)
    assert result == "Email: [EMAIL], Phone: [PHONE]"
    assert len(accepted) == 2


def test_overlapping_spans_secret_wins():
    """When a secret and a keyword overlap, the secret should win."""
    text = "sk-proj-abc123def456ghi789jkl"  # length 29
    spans = [
        # Keyword match that partially overlaps
        MaskSpan(start=10, end=29, replacement="[KEYWORD]", mask_type="keyword", priority=50, detector="custom"),
        # Secret match (covers full text)
        MaskSpan(start=0, end=29, replacement="[REDACTED_API_KEY]", mask_type="secret", priority=1, detector="sensitive_info"),
    ]
    result, accepted = merge_mask_spans(text, spans)
    assert result == "[REDACTED_API_KEY]"
    assert len(accepted) == 1
    assert accepted[0].mask_type == "secret"


def test_overlapping_picks_longer_span():
    """When two spans of the same type overlap, the longer one wins."""
    text = "alice@example.com"
    spans = [
        MaskSpan(start=0, end=17, replacement="[FULL]", mask_type="pii", priority=10, detector="sensitive_info"),
        MaskSpan(start=11, end=17, replacement="[PART]", mask_type="pii", priority=10, detector="sensitive_info"),
    ]
    result, accepted = merge_mask_spans(text, spans)
    assert result == "[FULL]"
    assert len(accepted) == 1


def test_overlapping_higher_confidence_wins_when_same_type_length():
    text = "alice@example.com"
    spans = [
        MaskSpan(start=0, end=17, replacement="[LOW]", mask_type="pii", priority=10, confidence=0.5, detector="a"),
        MaskSpan(start=0, end=17, replacement="[HIGH]", mask_type="pii", priority=10, confidence=0.95, detector="b"),
    ]
    result, accepted = merge_mask_spans(text, spans)
    assert result == "[HIGH]"
    assert len(accepted) == 1


def test_invalid_spans_filtered():
    text = "test"
    spans = [
        MaskSpan(start=5, end=3, replacement="[INVALID]", mask_type="pii", detector="test"),
        MaskSpan(start=0, end=2, replacement="[OK]", mask_type="pii", detector="test"),
    ]
    result, accepted = merge_mask_spans(text, spans)
    assert result == "[OK]st"
    assert len(accepted) == 1
