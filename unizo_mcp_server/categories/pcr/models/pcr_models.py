import time
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ---------- ENUMS ----------
class RepositoryType(str, Enum):
    CONTAINER = "container"
    PACKAGE = "package"
    GENERIC = "generic"


class ArtifactType(str, Enum):
    CONTAINER = "container"
    PACKAGE = "package"
    BLOB = "blob"


class TagType(str, Enum):
    TAG = "tag"
    BRANCH = "branch"
    SEMANTIC = "semantic"


# ---------- CORE MODELS ----------
class Pagination(BaseModel):
    total: Optional[int] = Field(None, description="Total number of items")
    limit: Optional[int] = Field(None, description="Number of items per page")
    offset: Optional[int] = Field(None, description="Offset for pagination")
    previous: Optional[int] = Field(None, description="Previous page offset")
    next: Optional[int] = Field(None, description="Next page offset")


class ResponseMetadata(BaseModel):
    requestId: Optional[str] = Field(None, description="Unique request identifier")
    timestamp: Optional[str] = Field(None, description="Response timestamp")
    version: Optional[str] = Field(None, description="API version")
    processingTime: Optional[int] = Field(None, description="Processing time in milliseconds")


class ErrorResponse(BaseModel):
    errorCode: str = Field(..., description="Error code", pattern=r"^AP-\d{7}$")
    errorMessage: str = Field(..., description="Error message")
    statusCode: Optional[int] = Field(None, description="HTTP status code")
    correlationId: Optional[str] = Field(None, description="Correlation ID")
    details: Optional[str] = Field(None, description="Additional error details")
    property: Optional[str] = Field(None, description="Property that caused the error")
    help: Optional[str] = Field(None, description="Help text")
    additionalInfo: Optional[List[Dict[str, str]]] = Field(None, description="Additional error information")


class AdditionalInfo(BaseModel):
    key: str = Field(..., description="Information key")
    value: str = Field(..., description="Information value")


class Link(BaseModel):
    rel: str = Field(..., description="Relationship type")
    href: str = Field(..., description="Link URI")
    method: str = Field(..., description="HTTP method")
    contentType: str = Field(default="application/json", description="Content type")
    authenticate: bool = Field(default=True, description="Authentication requirement")


class Avatar(BaseModel):
    original: Optional[str] = Field(None, description="Original avatar URI")
    xSmall: Optional[str] = Field(None, description="Extra small avatar URI")
    small: Optional[str] = Field(None, description="Small avatar URI")
    medium: Optional[str] = Field(None, description="Medium avatar URI")
    large: Optional[str] = Field(None, description="Large avatar URI")


class User(BaseModel):
    href: Optional[str] = Field(None, description="User URI")
    id: str = Field(..., description="User ID")
    firstName: Optional[str] = Field(None, description="User's first name")
    lastName: Optional[str] = Field(None, description="User's last name")
    avatar: Optional[Avatar] = Field(None, description="User's avatar information")


class ChangeLog(BaseModel):
    createdDateTime: str = Field(..., description="Creation timestamp")
    lastUpdatedDateTime: Optional[str] = Field(None, description="Last update timestamp")
    createdBy: Optional[User] = Field(None, description="Creator information")
    lastUpdatedBy: Optional[User] = Field(None, description="Last updater information")


# ---------- ORGANIZATION MODELS ----------
class OrganizationResponse(BaseModel):
    id: str = Field(..., description="Unique identifier of the organization", pattern=r"^[a-z0-9-]+$")
    login: str = Field(..., description="Login identifier for the organization", pattern=r"^[a-z0-9-]+$")
    fork: bool = Field(..., description="Whether the organization is a fork")
    changeLog: ChangeLog = Field(..., description="Audit trail of organization creation and modifications")


class OrganizationsResponse(BaseModel):
    data: List[OrganizationResponse] = Field(..., description="List of organizations")
    pagination: Optional[Pagination] = Field(None, description="Pagination information")


# ---------- REPOSITORY MODELS ----------
class RepositoryResponse(BaseModel):
    type: RepositoryType = Field(..., description="Type of the repository")
    id: str = Field(..., description="Unique identifier of the repository")
    name: str = Field(..., description="Name of the repository")
    description: Optional[str] = Field(None, description="Description of the repository")
    fullName: str = Field(..., description="Full name of the repository including organization prefix")
    fork: bool = Field(..., description="Whether the repository is a fork")
    language: Optional[str] = Field(None, description="Primary language of the repository")
    additionalInfo: Optional[List[AdditionalInfo]] = Field(None, description="Additional repository information")
    links: Optional[List[Link]] = Field(None, description="Related links")
    changeLog: ChangeLog = Field(..., description="Audit trail of repository creation and modifications")


class RepositoriesResponse(BaseModel):
    data: List[RepositoryResponse] = Field(..., description="List of repositories")
    pagination: Optional[Pagination] = Field(None, description="Pagination information")


# ---------- ARTIFACT MODELS ----------
class ArtifactResponse(BaseModel):
    href: str = Field(..., description="URI of the artifact")
    id: str = Field(..., description="Unique identifier of the artifact")
    type: ArtifactType = Field(..., description="Type of the artifact")
    name: str = Field(..., description="Name of the artifact")
    description: Optional[str] = Field(None, description="Description of the artifact")
    changeLog: ChangeLog = Field(..., description="Audit trail of artifact creation and modifications")


class ArtifactsResponse(BaseModel):
    data: List[ArtifactResponse] = Field(..., description="List of artifacts")
    pagination: Optional[Pagination] = Field(None, description="Pagination information")


# ---------- TAG MODELS ----------
class TagResponse(BaseModel):
    href: str = Field(..., description="URI of the tag")
    id: str = Field(..., description="Unique identifier of the tag")
    type: TagType = Field(..., description="Type of the tag")
    name: str = Field(..., description="Name of the tag")
    description: Optional[str] = Field(None, description="Description of the tag")
    changeLog: ChangeLog = Field(..., description="Audit trail of tag creation and modifications")


class TagsResponse(BaseModel):
    data: List[TagResponse] = Field(..., description="List of tags")
    pagination: Optional[Pagination] = Field(None, description="Pagination information")


# ---------- CONNECTOR MODELS ----------
class Connector(BaseModel):
    name: str


class Integration(BaseModel):
    id: str
    name: str


# ---------- API RESPONSE ----------
class APIResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    timestamp: float = Field(default_factory=time.time, description="Response timestamp")
    data: Optional[Any] = Field(None, description="Response data")
    error_details: Optional[Any] = Field(None, description="Error details")