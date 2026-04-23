from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class NodeState(str, Enum):
    PENDING = "pending"
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    DECOMMISSIONING = "decommissioning"
    DELETED = "deleted"
    ERROR = "error"


VALID_TRANSITIONS: dict[NodeState, list[NodeState]] = {
    NodeState.PENDING: [NodeState.PROVISIONING],
    NodeState.PROVISIONING: [NodeState.ACTIVE, NodeState.ERROR],
    NodeState.ACTIVE: [NodeState.DECOMMISSIONING],
    NodeState.DECOMMISSIONING: [NodeState.DELETED, NodeState.ERROR],
    NodeState.ERROR: [NodeState.PENDING],
    NodeState.DELETED: [],
}


def can_transition(current: NodeState, target: NodeState) -> bool:
    return target in VALID_TRANSITIONS.get(current, [])


class NodeBase(BaseModel):
    name: str
    region: str
    cpu: int = Field(gt=0)
    memory_gb: int = Field(gt=0)
    metadata: dict = Field(default_factory=dict)


class NodeCreate(NodeBase):
    pass


class NodeResponse(NodeBase):
    id: str
    state: NodeState
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None


class TransitionRequest(BaseModel):
    target_state: NodeState
    reason: Optional[str] = None
