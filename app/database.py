from datetime import datetime
from typing import Optional
from app.models import NodeState
import uuid


# In-memory store — swap for SQLAlchemy async session in production
_nodes: dict[str, dict] = {}


def create_node(name: str, region: str, cpu: int, memory_gb: int, metadata: dict) -> dict:
    node_id = str(uuid.uuid4())
    now = datetime.utcnow()
    node = {
        "id": node_id,
        "name": name,
        "region": region,
        "cpu": cpu,
        "memory_gb": memory_gb,
        "metadata": metadata,
        "state": NodeState.PENDING,
        "created_at": now,
        "updated_at": now,
        "error": None,
    }
    _nodes[node_id] = node
    return node


def get_node(node_id: str) -> Optional[dict]:
    return _nodes.get(node_id)


def list_nodes(region: Optional[str] = None, state: Optional[NodeState] = None) -> list[dict]:
    nodes = list(_nodes.values())
    if region:
        nodes = [n for n in nodes if n["region"] == region]
    if state:
        nodes = [n for n in nodes if n["state"] == state]
    return nodes


def update_node_state(node_id: str, state: NodeState, error: Optional[str] = None) -> Optional[dict]:
    node = _nodes.get(node_id)
    if not node:
        return None
    node["state"] = state
    node["error"] = error
    node["updated_at"] = datetime.utcnow()
    return node


def delete_node(node_id: str) -> bool:
    return _nodes.pop(node_id, None) is not None
