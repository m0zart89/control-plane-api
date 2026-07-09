# control-plane-api

API-first control plane prototype built with FastAPI.

## Concept

Models infrastructure resources as composable, lifecycle-aware objects.
Each resource has a defined state machine: `pending → provisioning → active → decommissioning → deleted`.

## Quickstart

```bash
docker compose up --build
```

- API: http://localhost:8000 (interactive docs at [/docs](http://localhost:8000/docs))
- Prometheus: http://localhost:9090 · Grafana: http://localhost:3000 (anonymous admin)

Create a node, provision it, watch the state machine:

```bash
# create (state: pending)
curl -s -X POST localhost:8000/nodes/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "node-1", "region": "eu-central", "cpu": 4, "memory_gb": 8}'

# request provisioning (async; node becomes active a couple of seconds later)
curl -s -X POST localhost:8000/nodes/<id>/transition \
  -H 'Content-Type: application/json' \
  -d '{"target_state": "provisioning"}'

# poll state / list by region
curl -s localhost:8000/nodes/<id>
curl -s 'localhost:8000/nodes/?region=eu-central&state=active'

# operational metrics per resource type
curl -s localhost:8000/metrics | grep controlplane_
```

Invalid transitions are rejected with `409` (e.g. `pending -> decommissioning`);
a background reconciler loop (30s interval) corrects drift between desired and actual state.

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

