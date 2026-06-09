"""GuardContext — the carrier object that flows through the detection pipeline."""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GuardContext:
    """Holds original + normalized text and all request metadata.

    Passed to every detector and eventually to the policy decision engine.
    """

    original_text: str
    normalized_text: str
    app_id: str
    tenant_id: str
    environment: str = "production"
    user_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    policy_id: str | None = None
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    started_at: float = field(default_factory=time.monotonic)

    @property
    def elapsed_ms(self) -> float:
        return (time.monotonic() - self.started_at) * 1000
