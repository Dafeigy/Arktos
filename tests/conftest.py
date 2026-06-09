"""Shared test fixtures."""

import pytest
from httpx import ASGITransport, AsyncClient

from arktos.app.detectors.injection.detector import InjectionDetector
from arktos.app.detectors.moderation.detector import ModerationDetector
from arktos.app.detectors.sensitive.detector import SensitiveInfoDetector
from arktos.app.main import create_app
from arktos.app.api.v1.inspect import register_detectors
from arktos.app.schemas.context import GuardContext


@pytest.fixture
def app():
    """Return a fresh FastAPI app instance for testing."""
    return create_app()


@pytest.fixture
async def client(app):
    """Return an async HTTP test client with detectors pre-registered."""
    # Manually register detectors — the app lifespan is skipped for test simplicity.
    # The audit writer is NOT started; audit events are silently dropped in tests.
    detectors = [
        InjectionDetector(is_pre_gate=True),
        SensitiveInfoDetector(),
        ModerationDetector(),
    ]
    register_detectors(detectors)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def guard_context():
    """Return a basic GuardContext for unit tests."""
    return GuardContext(
        original_text="Hello, world!",
        normalized_text="hello, world!",
        app_id="test-app",
        tenant_id="test-tenant",
        environment="testing",
    )
