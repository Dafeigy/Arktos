# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Arktos is an enterprise LLM input-side guardrails service — a Python service that inspects user input **before** it reaches a downstream LLM, checking for sensitive data leaks, prompt injection/jailbreak attacks, and content compliance violations. It returns one of three decisions: `Blocked`, `Masked`, or `Passed`.

## Tech Stack (Planned)

- **Language:** Python 3.11+
- **Web framework:** FastAPI
- **Validation:** Pydantic v2
- **Server:** Uvicorn (async, multi-worker)
- **Cache/config hot-reload:** Redis
- **Database:** PostgreSQL (audit logs, config persistence)
- **Observability:** Prometheus + structured JSON logging
- **Deployment:** Docker + Kubernetes

## Build, Test, and Run Commands

_Note: This project is in the pre-code planning phase. The following reflects the intended tooling from the development plan._

```bash
# Install dependencies (expect pyproject.toml / poetry or pip)
poetry install          # if using Poetry
pip install -e ".[dev]" # if using pip + setup.cfg/pyproject.toml

# Run the service (development)
uvicorn arktos.app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest                            # all tests
pytest tests/unit/                # unit tests only
pytest tests/unit/detectors/      # detector-specific tests
pytest -k "test_pii_detector"     # single test by name pattern

# Run regression suite (sample-based evaluation)
pytest tests/regression/          # evaluates accuracy/fpr/fnr against labeled samples

# Lint & format (once tooling is set up)
ruff check arktos/
ruff format arktos/
mypy arktos/

# Build Docker image
docker build -t arktos:latest .
```

## Architecture

Arktos is a **modular monolith** (phase 1) — not microservices. The detection pipeline is an async orchestration layer that fans out to pluggable detectors in parallel, then converges results through a policy decision engine.

### Request Flow

```
Client → FastAPI → Preprocessor → Schema Validator → Pipeline Orchestrator
                                                        ├─→ Rule Engine Detector
                                                        ├─→ PII Detector
                                                        ├─→ Injection/Jailbreak Detector
                                                        ├─→ Content Safety Detector
                                                        └─→ Custom Detectors
                                   Policy Decision Engine → Audit Logger → Response
```

### Three-State Decision Model

| Decision | Meaning |
|----------|---------|
| `Blocked` | Request rejected, do not call downstream LLM |
| `Masked`  | Request can proceed, but sensitive spans have been redacted |
| `Passed`  | Clean — original text can proceed unchanged |

Priority: `Blocked > Masked > Passed`. A single `Blocked` result from any detector overrides everything.

### Key Modules (per development plan)

```
arktos/
  app/
    api/            # FastAPI routes — POST /v1/inspect, GET /health
    core/           # Config, dependency injection, app factory
    orchestrator/   # Pipeline runner — parallel task dispatch, short-circuit, timeouts
    detectors/      # Pluggable detector implementations
      sensitive/    # PII/secrets detection (regex, dictionary)
      injection/    # Prompt injection & jailbreak detection
      moderation/   # Content safety / compliance
      custom/       # User-defined detectors
    policy/         # Policy decision engine, rule evaluation, mask span merging
    redaction/      # Text redaction/masking utilities
    audit/          # Async audit logging (trace, decisions, matched rules)
    storage/        # DB access layer, config persistence
    schemas/        # Pydantic models: requests, responses, detector results, MaskSpan
    utils/          # Shared helpers
  config/           # YAML/JSON config files
  rules/            # Rule definitions (regex patterns, keyword dictionaries, jailbreak templates)
    sensitive/
    injection/
    moderation/
    custom/
  tests/
    unit/
    integration/
    regression/     # Labeled sample evaluation suite
  docs/             # PRD, architecture, development plan
  scripts/          # Deployment, migration, benchmark scripts
```

### Detector Protocol

Every detector implements a uniform async interface returning `DetectorResult`:

- `SignalDetector` — returns `Blocked` / `Passed` signals (injection, jailbreak, content safety)
- `TransformDetector` — returns `Masked` / `Blocked` / `Passed` + `mask_spans` (PII, secrets)

Detectors **do not** decide the final response; they provide risk signals. The policy decision engine aggregates all results and produces the final `Blocked`/`Masked`/`Passed` verdict.

### Pipeline Stages

1. **pre_gate** — cheap, high-confidence blocking rules run first (high-risk keyword blacklist)
2. **parallel** — all main detectors run concurrently with independent timeouts
3. **post** — mask span merging, policy decision, audit log flush

Early short-circuit: if any pre_gate or parallel detector returns `should_short_circuit=True` with `Blocked`, remaining tasks are cancelled immediately.

### Mask Span Merging

When multiple detectors produce overlapping `MaskSpan` suggestions (e.g., email PII and keyword both match `alice@example.com`), a deterministic conflict resolver picks one winner per overlap cluster based on: priority > mask type rank (`secret` > `pii` > `internal_asset` > `keyword`) > span length > confidence. After resolving conflicts, the final `masked_text` is built in a single pass.

### Performance Targets

- P95 latency: < 150ms (rule-only path), < 400ms (with model-assisted detectors)
- 300+ concurrent requests
- Total request timeout budget: 500–1000ms
- Service availability: 99.9%

## Key Design Decisions from the Docs

- **No complex DSL for rules** — use structured JSON/YAML configs in the `rules/` directory, version-controlled alongside code.
- **No raw text in audit logs** — store only hashed/safe summaries; audit logs must themselves be sanitized.
- **Tenant/app isolation** — different business units use different policy configurations, not a single global rule set.
- **Stateless detectors** — detectors must be horizontally scalable; config is loaded from Redis or file.
- **MVP scope is narrow** — focus on `POST /v1/inspect` + sensitive data detection + prompt injection detection + basic moderation + file-based rules + audit logging.

## Design Documents

- [PRD](docs/arktos-prd.md) — product requirements, use cases, risk taxonomy, success metrics
- [Development Plan](docs/arktos-development-plan.md) — tech stack, module breakdown, phased milestones, testing strategy
- [Pipeline Architecture](docs/arktos-pipeline-architecture.md) — detailed pipeline design, detector protocol, mask merging algorithm, async execution model, performance targets
