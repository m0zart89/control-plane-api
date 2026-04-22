# control-plane-api

API-first control plane prototype built with FastAPI.

## Concept

Models infrastructure resources as composable, lifecycle-aware objects.
Each resource has a defined state machine: `pending → provisioning → active → decommissioning → deleted`.

## Design principles

- **API-first** — every infrastructure operation is a typed HTTP call, no direct DB or queue access
- **Async provisioning** — non-blocking operations with status polling and webhook callbacks
- **Reconciliation** — background loop detects and corrects drift between desired and actual state
- **Multi-region routing** — requests dispatched to regional conductors based on resource placement

## Stack

- FastAPI + Pydantic — typed API layer
- SQLAlchemy (async) — state persistence
- Celery / asyncio — background reconciliation workers
- Prometheus — operational metrics per resource type

## Background

Based on patterns from replacing queue-driven Lambda workflows with synchronous API orchestration.
Result: provisioning latency reduced from 17 min → 3 min by eliminating queue backpressure.

## Status

Prototype — extracting and documenting core patterns.

