import time
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


# ---------- ENUMS ----------
class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    DEBUG = "DEBUG"
    TRACE = "TRACE"


# ---------- CORE MODELS ----------
class Pagination(BaseModel):
    total: Optional[int] = Field(None, ge=0, description="Total number of elements")  # Fixed: ge instead of ge=1
    limit: Optional[int] = Field(None, ge=1, le=100, description="Number of items per page")
    offset: Optional[int] = Field(None, ge=0, description="Current page offset")  # Fixed: ge=0 instead of ge=1
    previous: Optional[int] = Field(None, ge=0, description="Previous page number")  # Fixed: ge=0 instead of ge=1
    next: Optional[int] = Field(None, ge=0, description="Next page number")  # Fixed: ge=0 instead of ge=1


class ChangeLog(BaseModel):
    createdDateTime: Optional[str] = Field(None, description="Timestamp when the log was created")
    lastUpdatedDateTime: Optional[str] = Field(None, description="Timestamp when the log was last updated")
    createdBy: Optional['User'] = Field(None, description="User who created the log")
    lastUpdatedBy: Optional['User'] = Field(None, description="User who last updated the log")


class User(BaseModel):
    href: Optional[str] = Field(None, description="User API endpoint URL")
    id: Optional[str] = Field(None, description="User unique identifier")
    firstName: Optional[str] = Field(None, description="User's first name")
    lastName: Optional[str] = Field(None, description="User's last name")
    avatar: Optional['Avatar'] = Field(None, description="User avatar information")


class Avatar(BaseModel):
    original: Optional[str] = Field(None, description="Original avatar URL")
    xSmall: Optional[str] = Field(None, description="Extra small avatar URL")
    small: Optional[str] = Field(None, description="Small avatar URL")
    medium: Optional[str] = Field(None, description="Medium avatar URL")
    large: Optional[str] = Field(None, description="Large avatar URL")


class LogMetadata(BaseModel):
    service: Optional[str] = Field(None, description="Service name")
    environment: Optional[str] = Field(None, description="Deployment environment")
    region: Optional[str] = Field(None, description="Geographic region")
    traceId: Optional[str] = Field(None, description="Distributed tracing ID")
    spanId: Optional[str] = Field(None, description="Span ID for tracing")
    hostname: Optional[str] = Field(None, description="Host where the log was generated")
    version: Optional[str] = Field(None, description="Service version")
    tags: Optional[List[str]] = Field(None, description="Additional tags for categorization")

    # FIXED: Use model_config instead of Config class for Pydantic V2
    model_config = {
        "json_schema_extra": {
            "example": {
                "service": "payment-service",
                "environment": "production",
                "region": "us-east-1",
                "traceId": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
                "spanId": "b7ad6b7169203331",
                "hostname": "payment-service-01",
                "version": "1.2.3",
                "tags": ["payment", "transaction", "timeout"]
            }
        }
    }


class LogResponse(BaseModel):
    id: str = Field(
        ...,
        description="Unique identifier of the log entry",
        pattern=r"^log-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-[a-z0-9]{6}$",  # FIXED: Use 'pattern' instead of 'regex'
        examples=["log-2024-01-01-12-00-00-abc123"]  # FIXED: Use 'examples' instead of 'example'
    )
    level: LogLevel = Field(..., description="Severity level of the log entry")
    message: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Detailed log message",
        examples=["Failed to process payment transaction: Connection timeout after 30s"]  # FIXED: Use 'examples'
    )
    source: str = Field(
        ...,
        pattern=r"^[a-z0-9-]+$",  # FIXED: Use 'pattern' instead of 'regex'
        description="Source of the log entry",
        examples=["payment-service"]  # FIXED: Use 'examples'
    )
    timestamp: str = Field(
        ...,
        description="Timestamp when the log was generated",
        examples=["2024-01-01T12:00:00Z"]  # FIXED: Use 'examples'
    )
    metadata: Optional[LogMetadata] = Field(None, description="Additional structured metadata about the log entry")
    changeLog: Optional[ChangeLog] = Field(None, description="Audit trail of log entry modifications")


class LogsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[LogResponse] = Field(..., description="List of log entries")


class ErrorDetails(BaseModel):
    property: Optional[str] = Field(None, description="Property related to the error")
    reason: Optional[str] = Field(None, description="Reason for the error")


class ErrorInfo(BaseModel):
    errorCode: str = Field(..., pattern=r"^AP-\d{7}$", description="Error code")  # FIXED: Use 'pattern'
    errorMessage: str = Field(..., description="Error message")
    statusCode: Optional[int] = Field(None, description="HTTP status code")
    correlationId: Optional[str] = Field(None, description="Correlation ID")
    details: Optional[str] = Field(None, description="Additional error details")
    property: Optional[str] = Field(None, description="Property related to the error")
    help: Optional[str] = Field(None, description="Help information")
    additionalInfo: Optional[List[ErrorDetails]] = Field(None, description="Additional error information")


class ResponseMetadata(BaseModel):
    requestId: Optional[str] = Field(None, description="Unique request identifier")
    timestamp: Optional[str] = Field(None, description="Response timestamp")
    version: Optional[str] = Field(None, description="API version")
    processingTime: Optional[int] = Field(None, description="Processing time in milliseconds")


# ---------- INTEGRATION MODELS ----------
class Connector(BaseModel):
    name: str = Field(..., description="Connector name")


class Integration(BaseModel):
    id: str = Field(..., description="Integration unique identifier")
    name: str = Field(..., description="Integration name")


# ---------- API RESPONSE ----------
class APIResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    timestamp: float = Field(default_factory=time.time, description="Response timestamp")
    data: Optional[Any] = Field(None, description="Response data")
    error_details: Optional[Any] = Field(None, description="Error details")


# Update forward references for Pydantic V2
User.model_rebuild()
ChangeLog.model_rebuild()