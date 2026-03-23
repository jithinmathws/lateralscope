from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NodeType(str, Enum):
    IDENTITY = "identity"      # Users, Service Accounts
    GROUP = "group"            # AD Groups, IAM Roles
    HOST = "host"              # Workstations, Servers
    DATA_ASSET = "data_asset"  # DBs, S3 Buckets, Secrets
    NETWORK = "network"        # Subnets, VPCs
    CROWN_JEWEL = "crown_jewel"


class EdgeType(str, Enum):
    # Identity / Access
    MEMBER_OF = "MEMBER_OF"
    ADMIN_ON = "ADMIN_ON"
    HAS_SESSION = "HAS_SESSION"  # Critical for lateral movement

    # Network / Remote Access
    CAN_RDP_TO = "CAN_RDP_TO"
    CAN_SSH_TO = "CAN_SSH_TO"
    NETWORK_REACHABLE = "NETWORK_REACHABLE"

    # Vulnerability / Exploitation
    EXPLOITS = "EXPLOITS"
    VULNERABLE_TO = "VULNERABLE_TO"

    # Cloud / Logical
    TRUSTS = "TRUSTS"
    OWNER_OF = "OWNER_OF"


class NodeData(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(..., min_length=1)
    type: NodeType
    label: str = Field(..., min_length=1)
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "label", mode="before")
    @classmethod
    def strip_string_fields(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("Field cannot be empty or whitespace.")
        return value


class EdgeData(BaseModel):
    source: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)
    type: EdgeType
    weight: float = Field(default=1.0, gt=0)
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source", "target", mode="before")
    @classmethod
    def strip_node_refs(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("Field cannot be empty or whitespace.")
        return value