"""Text preprocessing utilities."""

import re
import unicodedata


# Control characters that may be used for prompt injection obfuscation
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f​-‏ - ⁠-⁯﻿￰-￿]")

# Zero-width and invisible characters often used in bypass attempts
_INVISIBLE_CHARS = re.compile(r"[​-‏⁠-⁤⁪-⁯﻿]")


def normalize_text(text: str) -> tuple[str, bool]:
    """Apply Unicode NFKC normalization and flag suspicious characters.

    Returns (normalized_text, has_suspicious_chars).
    """
    has_suspicious = False

    # Detect zero-width / invisible chars before normalizing
    if _INVISIBLE_CHARS.search(text):
        has_suspicious = True

    # NFKC normalization (combines compatibility equivalents)
    normalized = unicodedata.normalize("NFKC", text)

    # Detect remaining control chars
    if _CONTROL_CHARS.search(normalized):
        has_suspicious = True

    # Strip excessive whitespace but preserve newlines
    normalized = normalized.strip()

    return normalized, has_suspicious


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to max_length, breaking at word boundary if possible."""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    # Try to break at the last space within the limit
    last_space = truncated.rfind(" ")
    if last_space > max_length // 2:
        return truncated[:last_space]
    return truncated
