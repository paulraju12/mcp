import time
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ResourceType(str, Enum):
    REPOSITORY = "REPOSITORY"
    PROJECT = "PROJECT"
    ORGANIZATION = "ORGANIZATION"
    USER = "USER"
    TEAM = "TEAM"
    ISSUE = "ISSUE"
    PULL_REQUEST = "PULL_REQUEST"
    BRANCH = "BRANCH"
    TAG = "TAG"
    COMMIT = "COMMIT"
    RELEASE = "RELEASE"


class APIResponse(BaseModel):
    """Standard API response wrapper"""
    status: str
    message: str
    timestamp: float = Field(default_factory=time.time)
    data: Optional[Any] = None
    error_details: Optional[Any] = None


class WatchType(str, Enum):
    HOOK = "HOOK"
    WEBHOOK = "WEBHOOK"
    EVENT = "EVENT"


class WatchConfig(BaseModel):
    url: str = Field(..., description="Webhook URL", example="https://smee.io/LfEhW8d1RijyTqf0")
    securedSSLRequired: Optional[bool] = Field(False, description="Whether SSL is required for the webhook")
    contentType: Optional[str] = Field("application/json", description="Content type of the webhook payload")
    secret: Optional[str] = Field(None, description="Secret for webhook signature verification")
    retryCount: Optional[int] = Field(None, ge=0, le=10, description="Number of retry attempts for failed deliveries")
    timeout: Optional[int] = Field(None, ge=1, le=300, description="Timeout in seconds for webhook delivery")
    headers: Optional[Dict[str, str]] = Field(None, description="Additional headers to be sent with the webhook")


class WatchResource(BaseModel):
    type: ResourceType = Field(..., description="Type of resource being watched")
    repository: Optional[Dict[str, str]] = Field(None, description="Repository identifier")
    organization: Optional[Dict[str, str]] = Field(None, description="Organization identifier")
    config: Optional[WatchConfig] = Field(None, description="Watch configuration")


class WatchRequest(BaseModel):
    name: str = Field(..., description="Name of the watch", example="web-gateway-service-watch github")
    description: Optional[str] = Field(None, description="Description of the watch")
    type: WatchType = Field(..., description="Type of watch")
    resource: WatchResource = Field(..., description="Resource being watched")


class WebhookRequest(BaseModel):
    """Webhook request model"""
    name: str = Field(..., description="Name of the webhook")
    description: Optional[str] = Field(None, description="Description of the webhook")
    url: str = Field(..., description="Webhook URL")
    events: Optional[List[str]] = Field(None, description="List of events to subscribe to")
    active: Optional[bool] = Field(True, description="Whether the webhook is active")
    secret: Optional[str] = Field(None, description="Secret for webhook signature verification")
    ssl_verification: Optional[bool] = Field(True, description="Whether to verify SSL certificates")
    content_type: Optional[str] = Field("application/json", description="Content type for webhook payloads")


class WebhookActionRequest(BaseModel):
    """Webhook action request model"""
    action: str = Field(..., description="Action to perform (e.g., 'test', 'ping', 'redeliver')")
    delivery_id: Optional[str] = Field(None, description="Delivery ID for redelivery actions")


class UpdateOperation(BaseModel):
    """JSON Patch operation for update requests"""
    op: str = Field(..., description="Operation type (replace, add, remove)")
    path: str = Field(..., description="JSON path to the field being updated")
    value: Optional[Any] = Field(None, description="New value for the field")


class UpdateRequest(BaseModel):
    """Update request containing list of operations"""
    operations: List[UpdateOperation] = Field(..., description="List of update operations")