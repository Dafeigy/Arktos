"""FastAPI application factory for Arktos."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from arktos.app.api.v1.health import router as health_router
from arktos.app.api.v1.inspect import register_detectors, router as inspect_router
from arktos.app.audit.logger import start_audit_writer, stop_audit_writer
from arktos.app.detectors.base import BaseDetector
from arktos.app.detectors.injection.detector import InjectionDetector
from arktos.app.detectors.moderation.detector import ModerationDetector
from arktos.app.detectors.sensitive.detector import SensitiveInfoDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_detectors() -> list[BaseDetector]:
    """Build the default detector suite.

    InjectionDetector runs as pre-gate (priority 1, can_short_circuit).
    SensitiveInfoDetector and ModerationDetector run in the parallel stage.
    """
    return [
        InjectionDetector(is_pre_gate=True),
        SensitiveInfoDetector(),
        ModerationDetector(),
    ]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # Startup
    logger.info("Arktos starting up...")
    await start_audit_writer()
    detectors = create_detectors()
    register_detectors(detectors)
    logger.info("Arktos ready")
    yield
    # Shutdown
    logger.info("Arktos shutting down...")
    await stop_audit_writer()
    logger.info("Arktos stopped")


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    app = FastAPI(
        title="Arktos",
        description="Enterprise LLM input guardrails service",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Register routes
    app.include_router(health_router)
    app.include_router(inspect_router)

    return app


# Module-level app instance for uvicorn
app = create_app()
