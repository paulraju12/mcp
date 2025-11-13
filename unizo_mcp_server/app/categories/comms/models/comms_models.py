import time
from enum import Enum
from typing import Optional, List, Dict, Any, Union,Callable
from pydantic import BaseModel, Field


# ---------- ENUMS ----------
class ChannelType(str, Enum):
    LIST = "LIST"
    CHANNEL = "CHANNEL"


class ChannelState(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class Visibility(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


# ---------- CORE MODELS ----------
class Pagination(BaseModel):
    total: Optional[int] = Field(None, description="Total number of elements")
    limit: Optional[int] = Field(None, description="Page size", ge=1, le=100)
    offset: Optional[int] = Field(None, description="Starting position", ge=0)
    previous: Optional[int] = Field(None, description="Previous page offset")
    next: Optional[int] = Field(None, description="Next page offset")


class ResponseMetadata(BaseModel):
    requestId: Optional[str] = Field(None, description="Unique request identifier")
    timestamp: Optional[str] = Field(None, description="Response timestamp")
    version: Optional[str] = Field(None, description="API version")
    processingTime: Optional[int] = Field(None, description="Processing time in milliseconds")


class ChangeLog(BaseModel):
    createdDateTime: Optional[str] = Field(None, description="Timestamp when the resource was created", format="date-time")
    lastUpdatedDateTime: Optional[str] = Field(None, description="Timestamp when the resource was last updated", format="date-time")


class ErrorResponse(BaseModel):
    errorCode: str = Field(..., description="Error code", pattern="^AP-\\d{7}$")
    errorMessage: str = Field(..., description="Error message")
    statusCode: Optional[int] = Field(None, description="HTTP status code")
    correlationId: Optional[str] = Field(None, description="Correlation ID")
    details: Optional[str] = Field(None, description="Additional error details")
    property: Optional[str] = Field(None, description="Property that caused the error")
    help: Optional[str] = Field(None, description="Help message")
    additionalInfo: Optional[List[Dict[str, str]]] = Field(None, description="Additional error information")


class Avatar(BaseModel):
    original: Optional[str] = Field(None, description="Original size avatar URL", format="uri")
    xSmall: Optional[str] = Field(None, description="Extra small avatar URL", format="uri")
    small: Optional[str] = Field(None, description="Small avatar URL", format="uri")
    medium: Optional[str] = Field(None, description="Medium avatar URL", format="uri")
    large: Optional[str] = Field(None, description="Large avatar URL", format="uri")


class User(BaseModel):
    href: Optional[str] = Field(None, description="User API endpoint URL", format="uri")
    id: str = Field(..., description="User unique identifier", format="uuid")
    firstName: Optional[str] = Field(None, description="User's first name")
    lastName: Optional[str] = Field(None, description="User's last name")
    avatar: Optional[Avatar] = Field(None, description="User avatar information")


class AttachmentField(BaseModel):
    title: str = Field(..., description="Name of the field")
    value: str = Field(..., description="Value of the field")
    short: Optional[bool] = Field(None, description="Whether the field should be displayed in a compact format")


class Attachment(BaseModel):
    id: str = Field(..., description="Unique identifier for the attachment")
    contentType: Optional[str] = Field(None, description="MIME type of the attachment")
    authorName: Optional[str] = Field(None, description="Name of the person who created the attachment")
    title: Optional[str] = Field(None, description="Title or name of the attachment")
    titleLink: Optional[str] = Field(None, description="URL to access the attachment", format="uri")
    text: Optional[str] = Field(None, description="Preview or description of the attachment content")
    fields: Optional[List[AttachmentField]] = Field(None, description="Additional metadata fields for the attachment")


class ChannelCommonModel(BaseModel):
    href: Optional[str] = Field(None, description="Channel API endpoint URL", format="uri")
    type: Optional[str] = Field(None, description="Channel type")
    id: str = Field(..., description="Channel unique identifier")
    name: str = Field(..., description="Channel name")


# ---------- ORGANIZATION MODELS ----------
class OrganizationResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the organization in the communications system")
    login: str = Field(..., description="Organization's login name or identifier")
    name: str = Field(..., description="Display name of the organization")
    url: Optional[str] = Field(None, description="Base URL for accessing the organization's communication platform", format="uri")
    changeLog: Optional[ChangeLog] = Field(None, description="Audit trail of organization creation and modifications")


class OrganizationsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[OrganizationResponse] = Field(..., description="List of organizations")


# ---------- CHANNEL MODELS ----------
class ChannelResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the channel in the communications system")
    name: str = Field(..., description="Name of the channel")
    description: Optional[str] = Field(None, description="Detailed description of the channel's purpose and content")
    changeLog: Optional[ChangeLog] = Field(None, description="Audit trail of channel creation and modifications")


class ChannelsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[ChannelResponse] = Field(..., description="List of channels")


# ---------- MESSAGE MODELS ----------
class MessageRequest(BaseModel):
    name: Optional[str] = Field(None, description="Subject or title of the message")
    messageBody: str = Field(..., description="Content of the message to be sent")
    attachments: Optional[List[Attachment]] = Field(None, description="Files or media to be attached to the message")


class MessageResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the message in the communications system")
    name: Optional[str] = Field(None, description="Subject or title of the message")
    messageBody: str = Field(..., description="Content of the message")
    attachments: Optional[List[Attachment]] = Field(None, description="Files or media attached to the message")
    changeLog: Optional[ChangeLog] = Field(None, description="Audit trail of message creation and modifications")


class MessagesResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[MessageResponse] = Field(..., description="List of messages")


# ---------- CONNECTOR AND INTEGRATION MODELS ----------
class Connector(BaseModel):
    name: str = Field(..., description="Connector name")


class Integration(BaseModel):
    id: str = Field(..., description="Integration ID")
    name: str = Field(..., description="Integration name")


# ---------- API RESPONSE ----------
class APIResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    timestamp: float = Field(default_factory=time.time, description="Response timestamp")
    data: Optional[Any] = Field(None, description="Response data")
    error_details: Optional[Any] = Field(None, description="Error details")