"""Load content moderation patterns from YAML."""

from pathlib import Path

import yaml

from arktos.app.core.config import settings
from arktos.app.core.exceptions import RuleLoadError


class ModerationPatterns:
    """Holds moderation keyword lists keyed by category."""

    def __init__(self):
        rules_path = settings.rules_dir / "moderation" / "patterns.yaml"
        if not rules_path.exists():
            raise RuleLoadError(f"Rules file not found: {rules_path}")

        with open(rules_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)

        if not data:
            raise RuleLoadError(f"Empty rules file: {rules_path}")

        # Strip metadata keys (detector, version) — the rest are categories
        self.categories: dict[str, dict] = {}
        for key, value in data.items():
            if key in ("detector", "version"):
                continue
            if isinstance(value, dict) and "keywords" in value:
                self.categories[key] = {
                    "severity": value.get("severity", "medium"),
                    "keywords": [kw.lower() for kw in value["keywords"]],
                }

    @property
    def all_keywords(self) -> set[str]:
        """Return a set of all unique keywords across all categories."""
        result: set[str] = set()
        for cat in self.categories.values():
            result.update(cat["keywords"])
        return result


# Singleton
_moderation_patterns: ModerationPatterns | None = None


def load_patterns() -> ModerationPatterns:
    global _moderation_patterns
    if _moderation_patterns is None:
        _moderation_patterns = ModerationPatterns()
    return _moderation_patterns
