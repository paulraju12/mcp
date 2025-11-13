import time
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field,RootModel


# ---------- CORE MODELS ----------
class Pagination(BaseModel):
    total: Optional[int] = Field(None, description="Total number of elements", le=100, ge=1)
    limit: Optional[int] = Field(None, description="Specify the page size in the query", le=100, ge=1)
    offset: Optional[int] = Field(None, description="Specify where to start a page", le=100, ge=1)
    previous: Optional[int] = Field(None, description="Go to next page", le=100, ge=1)
    next: Optional[int] = Field(None, description="Go to previous page", le=100, ge=1)


class ChangeLog(BaseModel):
    createdDateTime: Optional[str] = Field(None, description="Creation timestamp", format="date-time")
    lastUpdatedDateTime: Optional[str] = Field(None, description="Last update timestamp", format="date-time")
    createdBy: Optional['User'] = Field(None, description="User who created the resource")
    lastUpdatedBy: Optional['User'] = Field(None, description="User who last updated the resource")


class User(BaseModel):
    href: Optional[str] = Field(None, description="App URI", format="uri")
    id: Optional[str] = Field(None, description="User unique identifier", format="uuid")
    firstName: Optional[str] = Field(None, description="User's first name")
    lastName: Optional[str] = Field(None, description="User's last name")
    avatar: Optional['Avatar'] = Field(None, description="User avatar information")


class Avatar(BaseModel):
    original: Optional[str] = Field(None, description="Original avatar URI", format="uri")
    xSmall: Optional[str] = Field(None, description="Extra small avatar URI", format="uri")
    small: Optional[str] = Field(None, description="Small avatar URI", format="uri")
    medium: Optional[str] = Field(None, description="Medium avatar URI", format="uri")
    large: Optional[str] = Field(None, description="Large avatar URI", format="uri")


class ErrorDetail(BaseModel):
    property: Optional[str] = Field(None, description="Property that caused the error")
    reason: Optional[str] = Field(None, description="Reason for the error")


class ErrorItem(BaseModel):
    errorCode: str = Field(..., description="Error code", pattern=r"^AP-\d{7}$")
    errorMessage: str = Field(..., description="Error message")
    statusCode: Optional[int] = Field(None, description="HTTP status code")
    correlationId: Optional[str] = Field(None, description="Correlation identifier")
    details: Optional[str] = Field(None, description="Additional error details")
    property: Optional[str] = Field(None, description="Property related to error")
    help: Optional[str] = Field(None, description="Help information")
    additionalInfo: Optional[List[ErrorDetail]] = Field(None, description="Additional error information")


class ErrorList(RootModel[List[ErrorItem]]):
    """Error List response model"""
    root: List[ErrorItem] = Field(..., description="List of errors")


# ---------- VAULT CONFIG MODELS ----------
class VaultConfigRequest(BaseModel):
    integrationId: str = Field(..., description="Integration unique identifier", format="uuid")
    name: str = Field(..., description="Vault configuration name")


class VaultConfigResponse(BaseModel):
    id: Optional[str] = Field(None, description="Vault configuration unique identifier")
    value: Optional[str] = Field(None, description="Vault configuration value")
    name: Optional[str] = Field(None, description="Vault configuration name")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class VaultConfigsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[VaultConfigResponse]] = Field(None, description="List of vault configurations")


class ResponseMetadata(BaseModel):
    requestId: Optional[str] = Field(None, description="Unique request identifier")
    timestamp: Optional[str] = Field(None, description="Response timestamp")
    version: Optional[str] = Field(None, description="API version")
    processingTime: Optional[int] = Field(None, description="Processing time in milliseconds")


class VaultConfigsListResponse(BaseModel):
    data: List[VaultConfigResponse] = Field(..., description="List of vault configurations")
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    metadata: Optional[ResponseMetadata] = Field(None, description="Response metadata")


class VaultConfigDetailsResponse(BaseModel):
    data: VaultConfigResponse = Field(..., description="Vault configuration details")
    metadata: Optional[ResponseMetadata] = Field(None, description="Response metadata")


# Connector and Integration models for consistency
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


# Update forward references
User.model_rebuild()
ChangeLog.model_rebuild()