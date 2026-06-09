"""Mask span merging — conflict resolution and text rebuilding.

When multiple detectors produce overlapping MaskSpan suggestions, this module
resolves conflicts deterministically and rebuilds the final masked text.
"""

from arktos.app.schemas.detector import MaskSpan

# Mask type → priority rank for conflict resolution (lower wins)
MASK_TYPE_RANK: dict[str, int] = {
    "secret": 0,
    "pii": 1,
    "internal_asset": 2,
    "keyword": 3,
}


def _spans_overlap(a: MaskSpan, b: MaskSpan) -> bool:
    """Return True if two spans overlap (touching at boundary does not count)."""
    return not (a.end <= b.start or b.end <= a.start)


def _choose_winner(spans: list[MaskSpan]) -> MaskSpan:
    """Pick the winning span from a set of overlapping spans.

    Tie-breaking order (first wins):
      1. Lower priority (user-configured)
      2. Mask type rank (secret > pii > internal_asset > keyword)
      3. Longer span (covers more)
      4. Higher confidence
      5. Earlier start position
      6. Detector name (alphabetical — stable)
    """
    return min(
        spans,
        key=lambda s: (
            s.priority,
            MASK_TYPE_RANK.get(s.mask_type, 99),
            -(s.end - s.start),
            -s.confidence,
            s.start,
            s.detector,
        ),
    )


def merge_mask_spans(text: str, spans: list[MaskSpan]) -> tuple[str, list[MaskSpan]]:
    """Resolve overlapping MaskSpans and rebuild the masked text.

    Args:
        text: The normalized text that all spans reference.
        spans: Full list of MaskSpan suggestions from all detectors.

    Returns:
        (masked_text, accepted_spans) where accepted_spans are sorted by start.
    """
    if not spans:
        return text, []

    # Sort by start, then by length descending (longer first among same-start)
    sorted_spans = sorted(
        spans,
        key=lambda s: (
            s.start,
            -(s.end - s.start),
            -s.confidence,
        ),
    )

    accepted: list[MaskSpan] = []

    for candidate in sorted_spans:
        # Skip invalid spans
        if candidate.start >= candidate.end:
            continue
        if candidate.start < 0 or candidate.end > len(text):
            continue

        # Find overlapping already-accepted spans
        overlaps = [s for s in accepted if _spans_overlap(candidate, s)]

        if not overlaps:
            accepted.append(candidate)
            continue

        # Resolve conflict
        winner = _choose_winner([candidate, *overlaps])
        if winner is candidate:
            # Remove defeated overlapping spans
            accepted = [s for s in accepted if s not in overlaps]
            accepted.append(candidate)
        # else: candidate loses, do nothing

    # Sort accepted spans by start position for text rebuilding
    accepted.sort(key=lambda s: s.start)

    # Rebuild text
    chunks: list[str] = []
    cursor = 0
    for span in accepted:
        chunks.append(text[cursor : span.start])
        chunks.append(span.replacement)
        cursor = span.end
    chunks.append(text[cursor:])

    return "".join(chunks), accepted
