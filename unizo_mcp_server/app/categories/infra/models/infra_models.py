import time
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ResourceState(str, Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    TERMINATED = "TERMINATED"
    PENDING = "PENDING"
    ERROR = "ERROR"


class ComputeType(str, Enum):
    EC2 = "EC2"
    ECS = "ECS"
    LAMBDA = "LAMBDA"
    EKS = "EKS"


class ParentResourceType(str, Enum):
    VPC = "VPC"
    SUBNET = "SUBNET"
    CLUSTER = "CLUSTER"
    NAMESPACE = "NAMESPACE"


class Pagination(BaseModel):
    total: Optional[int] = Field(None, ge=0, description="Total number of elements")
    limit: Optional[int] = Field(None, ge=1, le=100, description="Number of items per page")
    offset: Optional[int] = Field(None, ge=0, description="Current page offset")
    previous: Optional[int] = Field(None, ge=0, description="Previous page number")
    next: Optional[int] = Field(None, ge=0, description="Next page number")


class ChangeLog(BaseModel):
    createdDateTime: Optional[str] = Field(None, description="Creation timestamp")
    lastUpdatedDateTime: Optional[str] = Field(None, description="Last update timestamp")
    createdBy: Optional['User'] = Field(None, description="User who created")
    lastUpdatedBy: Optional['User'] = Field(None, description="User who last updated")


class Avatar(BaseModel):
    original: Optional[str] = Field(None, description="Original avatar URL")
    xSmall: Optional[str] = Field(None, description="Extra small avatar URL")
    small: Optional[str] = Field(None, description="Small avatar URL")
    medium: Optional[str] = Field(None, description="Medium avatar URL")
    large: Optional[str] = Field(None, description="Large avatar URL")


class User(BaseModel):
    href: Optional[str] = Field(None, description="User resource URI")
    id: Optional[str] = Field(None, description="User identifier")
    firstName: Optional[str] = Field(None, description="User's first name")
    lastName: Optional[str] = Field(None, description="User's last name")
    avatar: Optional[Avatar] = Field(None, description="User avatar")


class AccountResponse(BaseModel):
    id: Optional[str] = Field(None, description="Account ID")
    name: Optional[str] = Field(None, description="Account name")
    login: Optional[str] = Field(None, description="Account login")
    url: Optional[str] = Field(None, description="Account URL")
    avatarUrl: Optional[str] = Field(None, description="Account avatar URL")
    description: Optional[str] = Field(None, description="Account description")
    type: Optional[str] = Field(None, description="Account type")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log")


class AccountsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[AccountResponse]] = Field(None, description="Accounts data")


class CollectionResponse(BaseModel):
    id: Optional[str] = Field(None, description="Collection ID")
    name: Optional[str] = Field(None, description="Collection name")
    login: Optional[str] = Field(None, description="Collection login")
    url: Optional[str] = Field(None, description="Collection URL")
    avatarUrl: Optional[str] = Field(None, description="Collection avatar URL")
    description: Optional[str] = Field(None, description="Collection description")
    type: Optional[str] = Field(None, description="Collection type")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log")


class CollectionsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[CollectionResponse]] = Field(None, description="Collections data")


class UserResponse(BaseModel):
    id: Optional[str] = Field(None, description="User unique identifier")
    firstName: Optional[str] = Field(None, description="User's first name")
    lastName: Optional[str] = Field(None, description="User's last name")
    changeLog: Optional[ChangeLog] = Field(None, description="Audit trail")


class UsersResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[UserResponse]] = Field(None, description="Users data")


class ComputeDetailMetaData(BaseModel):
    cpuCores: Optional[str] = Field(None, description="CPU cores")
    memory: Optional[str] = Field(None, description="Memory size in GB")
    storage: Optional[str] = Field(None, description="Storage size in GB")
    os: Optional[str] = Field(None, description="Operating system")
    runtime: Optional[str] = Field(None, description="Runtime environment")
    instanceClass: Optional[str] = Field(None, description="Instance class")


class ComputeDetail(BaseModel):
    type: Optional[ComputeType] = Field(None, description="Compute resource type")
    metaData: Optional[ComputeDetailMetaData] = Field(None, description="Compute metadata")


class ParentResource(BaseModel):
    id: Optional[str] = Field(None, description="Parent resource ID")
    type: Optional[ParentResourceType] = Field(None, description="Parent resource type")


class UserCommonModel(BaseModel):
    href: Optional[str] = Field(None, description="User resource URI")
    type: Optional[str] = Field(None, description="User type")
    id: Optional[str] = Field(None, description="User ID")
    name: Optional[str] = Field(None, description="User name")


class ResourceResponse(BaseModel):
    id: Optional[str] = Field(None, description="Resource unique identifier")
    name: Optional[str] = Field(None, description="Resource name")
    state: Optional[ResourceState] = Field(None, description="Resource state")
    region: Optional[str] = Field(None, description="Geographic region")
    computeDetail: Optional[ComputeDetail] = Field(None, description="Compute details")
    parentResource: Optional[ParentResource] = Field(None, description="Parent resource")
    user: Optional[UserCommonModel] = Field(None, description="Resource owner")
    changeLog: Optional[ChangeLog] = Field(None, description="Audit trail")


class ResourcesResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[ResourceResponse]] = Field(None, description="Resources data")


class ErrorInfo(BaseModel):
    errorCode: str = Field(..., pattern=r"^AP-\d{7}$", description="Error code")
    errorMessage: str = Field(..., description="Error message")
    statusCode: Optional[int] = Field(None, description="HTTP status code")
    correlationId: Optional[str] = Field(None, description="Correlation ID")
    details: Optional[str] = Field(None, description="Additional details")
    property: Optional[str] = Field(None, description="Property with error")
    help: Optional[str] = Field(None, description="Help information")


# Integration models for connector discovery
class Connector(BaseModel):
    name: str = Field(..., description="Connector name")


class Integration(BaseModel):
    id: str = Field(..., description="Integration ID")
    name: str = Field(..., description="Integration name")


# Update forward references
User.model_rebuild()
ChangeLog.model_rebuild()