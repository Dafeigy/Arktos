"""Load and compile sensitive-info detection patterns from YAML."""

import re
from pathlib import Path

import yaml

from arktos.app.core.config import settings
from arktos.app.core.exceptions import RuleLoadError


class CompiledPattern:
    """A compiled regex pattern with its metadata for PII detection."""

    def __init__(self, pattern_def: dict):
        self.name: str = pattern_def["name"]
        self.display: str = pattern_def.get("display", self.name)
        self.regex: re.Pattern = re.compile(pattern_def["regex"], re.IGNORECASE | re.MULTILINE)
        self.mask_type: str = pattern_def.get("mask_type", "pii")
        self.priority: int = pattern_def.get("priority", 10)
        self.confidence: float = pattern_def.get("confidence", 0.8)
        self.replacement: str = pattern_def.get("replacement", "[REDACTED]")


def load_patterns() -> list[CompiledPattern]:
    """Load and compile all patterns from the sensitive info rules file."""
    rules_path = settings.rules_dir / "sensitive" / "patterns.yaml"
    if not rules_path.exists():
        raise RuleLoadError(f"Rules file not found: {rules_path}")

    with open(rules_path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    if not data or "patterns" not in data:
        raise RuleLoadError(f"Invalid rules file: {rules_path} (missing 'patterns' key)")

    compiled = []
    for pattern_def in data["patterns"]:
        try:
            compiled.append(CompiledPattern(pattern_def))
        except re.error as exc:
            raise RuleLoadError(
                f"Invalid regex in {rules_path}, pattern '{pattern_def.get('name', 'unknown')}': {exc}"
            ) from exc

    return compiled
