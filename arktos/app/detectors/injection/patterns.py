"""Load injection/jailbreak detection patterns from YAML."""

import re
from pathlib import Path

import yaml

from arktos.app.core.config import settings
from arktos.app.core.exceptions import RuleLoadError


class InjectionPatterns:
    """Holds the compiled injection detection patterns (keywords + regexes)."""

    def __init__(self):
        rules_path = settings.rules_dir / "injection" / "patterns.yaml"
        if not rules_path.exists():
            raise RuleLoadError(f"Rules file not found: {rules_path}")

        with open(rules_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)

        if not data:
            raise RuleLoadError(f"Empty rules file: {rules_path}")

        # Pre-gate: high-confidence keywords (lowercased for case-insensitive matching)
        pre_gate = data.get("pre_gate", {})
        self.pre_gate_keywords: list[str] = [
            kw.lower() for kw in pre_gate.get("keywords", [])
        ]
        self.pre_gate_regexes: list[tuple[str, re.Pattern, float]] = []
        for r in pre_gate.get("regexes", []):
            try:
                self.pre_gate_regexes.append(
                    (r["display"], re.compile(r["regex"], re.IGNORECASE), r.get("confidence", 0.9))
                )
            except re.error as exc:
                raise RuleLoadError(f"Invalid pre-gate regex '{r.get('display')}': {exc}") from exc

        # Standard: lower-confidence patterns
        standard = data.get("standard", {})
        self.standard_keywords: list[str] = [
            kw.lower() for kw in standard.get("keywords", [])
        ]
        self.standard_regexes: list[tuple[str, re.Pattern, float]] = []
        for r in standard.get("regexes", []):
            try:
                self.standard_regexes.append(
                    (r["display"], re.compile(r["regex"], re.IGNORECASE), r.get("confidence", 0.7))
                )
            except re.error as exc:
                raise RuleLoadError(f"Invalid standard regex '{r.get('display')}': {exc}") from exc


# Singleton loaded at import time
_injection_patterns: InjectionPatterns | None = None


def load_patterns() -> InjectionPatterns:
    global _injection_patterns
    if _injection_patterns is None:
        _injection_patterns = InjectionPatterns()
    return _injection_patterns
