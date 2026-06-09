"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Settings:
    """Arktos settings with sensible defaults for local development."""

    # Server
    host: str = field(default_factory=lambda: os.getenv("ARKTOS_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("ARKTOS_PORT", "8000")))

    # Timeouts (ms)
    request_timeout_ms: int = field(
        default_factory=lambda: int(os.getenv("ARKTOS_REQUEST_TIMEOUT_MS", "1000"))
    )
    detector_timeout_ms: int = field(
        default_factory=lambda: int(os.getenv("ARKTOS_DETECTOR_TIMEOUT_MS", "500"))
    )

    # Rules directory — relative to project root or absolute
    rules_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("ARKTOS_RULES_DIR", str(Path(__file__).parent.parent.parent.parent / "rules"))
        )
    )

    # Text limits
    max_text_length: int = 32768

    # Audit
    audit_enabled: bool = field(
        default_factory=lambda: os.getenv("ARKTOS_AUDIT_ENABLED", "true").lower() == "true"
    )


# Singleton
settings = Settings()
