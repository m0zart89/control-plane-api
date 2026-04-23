from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import Optional
from app.models import NodeCreate, NodeResponse, NodeState, TransitionRequest, can_transition
from app import database, metrics
import asyncio

router = APIRouter(prefix="/nodes", tags=["nodes"])


async def _run_provisioning(node_id: str):
    await asyncio.sleep(2)  # simulate provisioning work
    node = database.get_node(node_id)
    if node and node["state"] == NodeState.PROVISIONING:
        database.update_node_state(node_id, NodeState.ACTIVE)
        metrics.PROVISIONING_DURATION.labels(region=node["region"]).observe(2.0)
        metrics.NODES_TOTAL.labels(state="active", region=node["region"]).inc()
        metrics.NODES_TOTAL.labels(state="provisioning", region=node["region"]).dec()


async def _run_decommission(node_id: str):
    await asyncio.sleep(1)
    node = database.get_node(node_id)
    if node and node["state"] == NodeState.DECOMMISSIONING:
        database.update_node_state(node_id, NodeState.DELETED)
        metrics.NODES_TOTAL.labels(state="decommissioning", region=node["region"]).dec()


@router.post("/", response_model=NodeResponse, status_code=201)
async def create_node(payload: NodeCreate):
    node = database.create_node(**payload.model_dump())
    metrics.NODES_TOTAL.labels(state="pending", region=node["region"]).inc()
    return node


@router.get("/", response_model=list[NodeResponse])
async def list_nodes(
    region: Optional[str] = Query(None),
    state: Optional[NodeState] = Query(None),
):
    return database.list_nodes(region=region, state=state)


@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(node_id: str):
    node = database.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.post("/{node_id}/transition", response_model=NodeResponse)
async def transition_node(node_id: str, body: TransitionRequest, background_tasks: BackgroundTasks):
    node = database.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    if not can_transition(node["state"], body.target_state):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot transition from {node['state']} to {body.target_state}",
        )

    database.update_node_state(node_id, body.target_state)
    metrics.STATE_TRANSITIONS.labels(
        from_state=node["state"], to_state=body.target_state
    ).inc()

    if body.target_state == NodeState.PROVISIONING:
        background_tasks.add_task(_run_provisioning, node_id)
    elif body.target_state == NodeState.DECOMMISSIONING:
        background_tasks.add_task(_run_decommission, node_id)

    return database.get_node(node_id)


@router.delete("/{node_id}", status_code=204)
async def delete_node(node_id: str):
    node = database.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    if node["state"] not in (NodeState.PENDING, NodeState.ERROR, NodeState.DELETED):
        raise HTTPException(status_code=409, detail="Node must be in pending/error/deleted state to remove")
    database.delete_node(node_id)
