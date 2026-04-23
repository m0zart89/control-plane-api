"""
Background reconciliation loop.
Detects nodes stuck in transitional states and moves them to ERROR
so operators (or automation) can retry.
"""
import asyncio
from datetime import datetime, timedelta
from app import database, metrics
from app.models import NodeState

STUCK_THRESHOLD = timedelta(minutes=10)

TRANSITIONAL_STATES = {NodeState.PROVISIONING, NodeState.DECOMMISSIONING}


async def reconcile_once():
    metrics.RECONCILER_RUNS.inc()
    now = datetime.utcnow()

    for node in database.list_nodes():
        if node["state"] not in TRANSITIONAL_STATES:
            continue

        age = now - node["updated_at"]
        if age > STUCK_THRESHOLD:
            database.update_node_state(
                node["id"],
                NodeState.ERROR,
                error=f"stuck in {node['state']} for {int(age.total_seconds())}s",
            )
            metrics.RECONCILER_DRIFT.labels(state=node["state"]).inc()


async def reconciler_loop(interval_seconds: int = 30):
    while True:
        try:
            await reconcile_once()
        except Exception as exc:
            # log and continue — reconciler must not crash the process
            print(f"reconciler error: {exc}")
        await asyncio.sleep(interval_seconds)
