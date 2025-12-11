from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel


class ProjectResourceKind(StrEnum):
    STORAGE_BUCKET = "StorageBucket"
    SECRET = "Secret"
    DATABASE = "Database"


class ProjectResourceState(StrEnum):
    PENDING = "Pending"
    AVAILABLE = "Available"
    ERROR = "Error"


# API response model - what clients see
class ProjectResourceStatus(BaseModel):
    kind: ProjectResourceKind
    name: str
    status: ProjectResourceState = ProjectResourceState.PENDING
    aws_id: str | None = None
    description: str | None = None


# Internal DynamoDB model - for persistence layer
class ProjectResourceRecord(BaseModel):
    user_id: str  # PK
    resource_id: str  # SK = f"{project_name}#{resource_kind}#{resource_name}"
    project_name: str
    resource_name: str
    resource_kind: ProjectResourceKind
    status: ProjectResourceState = ProjectResourceState.PENDING
    aws_id: str | None = None
    description: str | None = None

    def to_api_response(self, hide_aws_id: bool = False) -> ProjectResourceStatus:
        """Convert to API response model."""
        return ProjectResourceStatus(
            kind=self.resource_kind,
            name=self.resource_name,
            status=self.status,
            aws_id=None if hide_aws_id else self.aws_id,
            description=self.description,
        )


class PortMapping(BaseModel):
    container_port: int
    host_port: int
    protocol: Literal["tcp", "udp"] = "tcp"


class ProjectRunningStatus(BaseModel):
    current: Literal["Pending", "Running", "Stopped", "Error"] = "Pending"
    deployment_revision: int | None = None
    last_updated: str | None = None
    public_ip: str | None = None

    port_mappings: list[PortMapping] | None = None
    cpu: str | None = None
    memory: str | None = None


class ProviderConfig(BaseModel):
    provider: Literal["aws"] = "aws"
    region: str | None = "eu-west-2"


class GetHealthResponse(BaseModel):
    status: str
    details: dict[str, Any] = {}


class PutProjectResponse(BaseModel):
    deployment_id: str
    status: str


class PutSecretValueRequest(BaseModel):
    secret_name: str
    secret_string: str


class PostDeploymentResponse(BaseModel):
    revision: int
    image: str
    status: str
    push_token: str | None = None
    error: str | None = None


class GetProjectResponse(BaseModel):
    name: str
    kind: Literal["Service"] = "Service"
    provisioning_state: str
    url: str | None = None
    running_status: ProjectRunningStatus
    resources: list[ProjectResourceStatus]
    port_mappings: list[PortMapping]
    cloud_provider: ProviderConfig
    cpu: str
    memory: str


class ListProjectsResponse(BaseModel):
    projects: list[GetProjectResponse]


class StorageBucketResource(BaseModel):
    kind: Literal["StorageBucket"]
    name: str


class SecretResource(BaseModel):
    kind: Literal["Secret"]
    name: str
    value_string: str | None = None


class DatabaseResource(BaseModel):
    kind: Literal["Database"]
    name: str


class PutProjectRequest(BaseModel):
    kind: Literal["Service"]
    name: str
    resources: list[StorageBucketResource | SecretResource | DatabaseResource] = []
    cloud_provider: ProviderConfig = ProviderConfig()
    port_mappings: list[PortMapping] = [
        PortMapping(container_port=8080, host_port=8080),
    ]
    cpu: str = "256"
    memory: str = "512"


class GetLogsResponse(BaseModel):
    logs: list[str]


class ListBucketKeysResponse(BaseModel):
    keys: list[str]
