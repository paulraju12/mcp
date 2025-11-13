import time
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ---------- ENUMS ----------
class CollectionType(str, Enum):
    PROJECT = "Project"
    SPRINT = "Sprint"
    EPIC = "Epic"
    COMPONENT = "Component"
    TEAM = "Team"

class CollectionStatus(str, Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"
    COMPLETED = "Completed"

class TicketType(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"
    SECURITY = "security"
    ENHANCEMENT = "enhancement"

class TicketStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    EDITOR = "editor"

class LinkType(str, Enum):
    BLOCKS = "blocks"
    IS_BLOCKED_BY = "is_blocked_by"
    RELATES_TO = "relates_to"
    DUPLICATES = "duplicates"
    IS_DUPLICATED_BY = "is_duplicated_by"
    CAUSES = "causes"
    IS_CAUSED_BY = "is_caused_by"
    CLONES = "clones"
    IS_CLONED_BY = "is_cloned_by"
    PARENT = "parent"
    CHILD = "child"

# ---------- BASE MODELS ----------
class Pagination(BaseModel):
    total_items: Optional[int] = Field(None, description="Total number of items available")
    item_count: Optional[int] = Field(None, description="Number of items in the current page")
    items_per_page: Optional[int] = Field(None, description="Number of items per page")
    total_pages: Optional[int] = Field(None, description="Total number of pages available")
    current_page: Optional[int] = Field(None, description="Current page number")
    # Legacy fields for backward compatibility
    total: Optional[int] = Field(None, description="Total number of items available")
    limit: Optional[int] = Field(None, description="Maximum number of items per page")
    offset: Optional[int] = Field(None, description="Starting position of the current page")
    previous: Optional[int] = Field(None, description="Starting position of the previous page")
    next: Optional[int] = Field(None, description="Starting position of the next page")

class ChangeLog(BaseModel):
    created_date_time: Optional[str] = Field(None, alias="createdDateTime", description="Timestamp when the resource was created")
    last_updated_date_time: Optional[str] = Field(None, alias="lastUpdatedDateTime", description="Timestamp when the resource was last updated")

class Avatar(BaseModel):
    original: Optional[str] = Field(None, description="Original high-resolution avatar image")
    x_small: Optional[str] = Field(None, alias="xSmall", description="Extra small avatar image (32x32 pixels)")
    small: Optional[str] = Field(None, description="Small avatar image (64x64 pixels)")
    medium: Optional[str] = Field(None, description="Medium avatar image (128x128 pixels)")
    large: Optional[str] = Field(None, description="Large avatar image (256x256 pixels)")

class User(BaseModel):
    href: Optional[str] = Field(None, description="API endpoint URL for the user")
    id: str = Field(..., description="Unique identifier for the user")
    email: Optional[str] = Field(None, description="User's email address")
    first_name: Optional[str] = Field(None, alias="firstName", description="User's first name")
    last_name: Optional[str] = Field(None, alias="lastName", description="User's last name")
    username: Optional[str] = Field(None, description="User's unique username")
    status: Optional[UserStatus] = Field(None, description="Account status of the user")
    role: Optional[UserRole] = Field(None, description="Role of the user in the system")
    last_login: Optional[str] = Field(None, alias="lastLogin", description="Timestamp of the user's last login")
    created_at: Optional[str] = Field(None, alias="createdAt", description="Timestamp when the user account was created")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="Timestamp when the user account was last updated")
    avatar: Optional[Avatar] = Field(None, description="Avatar URLs in different sizes")

class UserResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the user")
    email: Optional[str] = Field(None, description="User's email address")
    first_name: Optional[str] = Field(None, alias="firstName", description="User's first name")
    last_name: Optional[str] = Field(None, alias="lastName", description="User's last name")
    username: Optional[str] = Field(None, description="User's unique username")
    status: Optional[UserStatus] = Field(None, description="Account status of the user")
    role: Optional[UserRole] = Field(None, description="Role of the user in the system")
    last_login: Optional[str] = Field(None, alias="lastLogin", description="Timestamp of the user's last login")
    created_at: Optional[str] = Field(None, alias="createdAt", description="Timestamp when the user account was created")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="Timestamp when the user account was last updated")

class UsersResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[UserResponse] = Field(..., description="List of users")

# ---------- ORGANIZATION MODELS ----------
class Organization(BaseModel):
    id: str = Field(..., description="Unique identifier for the organization")
    name: Optional[str] = Field(None, description="Name of the organization")
    description: Optional[str] = Field(None, description="Detailed description of the organization")
    login: Optional[str] = Field(None, description="Organization's login name or identifier")
    target_url: Optional[str] = Field(None, alias="targetUrl", description="API URL for accessing the organization's resources")
    avatar_url: Optional[str] = Field(None, alias="avatarUrl", description="URL to the organization's avatar or logo")
    change_log: Optional[ChangeLog] = Field(None, alias="changeLog", description="Audit trail of organization changes")

class OrganizationsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[Organization] = Field(..., description="List of organizations")

# ---------- COLLECTION MODELS ----------
class CollectionStatistics(BaseModel):
    total_tickets: Optional[int] = Field(None, alias="totalTickets", description="Total number of tickets in the collection")
    open_tickets: Optional[int] = Field(None, alias="openTickets", description="Number of open tickets")
    completed_tickets: Optional[int] = Field(None, alias="completedTickets", description="Number of completed tickets")
    progress: Optional[float] = Field(None, description="Percentage of completed tickets")

class Collection(BaseModel):
    id: str = Field(..., description="Unique identifier for the collection")
    name: str = Field(..., description="Full name of the collection including organization prefix")
    description: Optional[str] = Field(None, description="Detailed description of the collection")
    key: Optional[str] = Field(None, description="Unique key identifier for the collection")
    owner: Optional[str] = Field(None, description="Name of the organization that owns the collection")
    access_level: Optional[bool] = Field(None, alias="accessLevel", description="Whether the collection has restricted access")
    target_url: Optional[str] = Field(None, alias="targetUrl", description="API endpoint URL for accessing the collection")
    type: CollectionType = Field(..., description="Type of collection")
    status: Optional[CollectionStatus] = Field(None, description="Current operational status")
    members: Optional[List[User]] = Field(None, description="Users who have access to the collection")
    start_date: Optional[str] = Field(None, alias="startDate", description="When the collection becomes active")
    end_date: Optional[str] = Field(None, alias="endDate", description="When the collection is scheduled to end")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")
    statistics: Optional[CollectionStatistics] = Field(None, description="Statistics about the collection's tickets")
    change_log: Optional[ChangeLog] = Field(None, alias="changeLog", description="Audit trail of collection changes")

class CollectionsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[Collection] = Field(..., description="List of collections")

class CollectionCreateRequest(BaseModel):
    name: str = Field(..., description="Display name of the collection")
    description: Optional[str] = Field(None, description="Detailed description of the collection's purpose")
    type: CollectionType = Field(..., description="Type of collection")
    owner_id: Optional[str] = Field(None, alias="ownerId", description="ID of the user who will own the collection")
    member_ids: Optional[List[str]] = Field(None, alias="memberIds", description="IDs of users who will have access")
    start_date: Optional[str] = Field(None, alias="startDate", description="When the collection starts")
    end_date: Optional[str] = Field(None, alias="endDate", description="When the collection ends")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")
    parent_id: Optional[str] = Field(None, alias="parentId", description="ID of the parent collection if this is a sub-collection")

# ---------- TICKET MODELS ----------
class TicketCreateRequest(BaseModel):
    name: str = Field(..., description="Short summary or title of the ticket")
    description: str = Field(..., description="Detailed description of the ticket's purpose, requirements, and acceptance criteria")
    type: TicketType = Field(..., description="Type of ticket")
    assignee_ids: Optional[List[str]] = Field(None, alias="assigneeIds", description="IDs of users to assign to the ticket")
    labels: Optional[List[str]] = Field(None, description="Tags or categories for the ticket")
    priority: Optional[TicketPriority] = Field(None, description="Importance level of the ticket")
    due_date: Optional[str] = Field(None, alias="dueDate", description="Target completion date for the ticket")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata for the ticket")

class TicketUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Short summary or title of the ticket")
    description: Optional[str] = Field(None, description="Detailed description of the ticket's purpose, requirements, and acceptance criteria")
    type: Optional[TicketType] = Field(None, description="Type of ticket")
    assignee_ids: Optional[List[str]] = Field(None, alias="assigneeIds", description="IDs of users to assign to the ticket")
    labels: Optional[List[str]] = Field(None, description="Tags or categories for the ticket")
    priority: Optional[TicketPriority] = Field(None, description="Importance level of the ticket")
    due_date: Optional[str] = Field(None, alias="dueDate", description="Target completion date for the ticket")
    status: Optional[TicketStatus] = Field(None, description="Current state of the ticket")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata for the ticket")

class CreateTicketBulkRequest(BaseModel):
    tickets: List[TicketCreateRequest] = Field(..., min_items=1, max_items=100, description="Array of tickets to be created in bulk")
    notify: Optional[bool] = Field(False, description="Whether to send notifications for the created tickets")

class TicketLinkRequest(BaseModel):
    source_ticket_id: str = Field(..., alias="sourceTicketId", description="The ID of the source ticket in the link relationship")
    target_ticket_id: str = Field(..., alias="targetTicketId", description="The ID of the target ticket in the link relationship")
    link_type: LinkType = Field(..., alias="linkType", description="The type of relationship between the tickets")
    comment: Optional[str] = Field(None, description="Optional comment about the link")

class TicketData(BaseModel):
    name: str = Field(..., description="Ticket name/title")
    description: Optional[str] = Field(None, description="Ticket description")
    status: Optional[TicketStatus] = Field(None, description="Ticket status")
    priority: Optional[TicketPriority] = Field(None, description="Ticket priority")
    type: Optional[TicketType] = Field(None, description="Ticket type")
    assignee_ids: Optional[List[str]] = Field(None, alias="assigneeIds", description="IDs of users to assign to the ticket")
    labels: Optional[List[str]] = Field(None, description="Tags or categories for the ticket")
    due_date: Optional[str] = Field(None, alias="dueDate", description="Target completion date for the ticket")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")

class TicketSummary(BaseModel):
    id: str = Field(..., description="Unique identifier for the ticket")
    name: str = Field(..., description="Short summary or title of the ticket")
    type: str = Field(..., description="Type of ticket")
    status: str = Field(..., description="Current state of the ticket")
    description: Optional[str] = Field(None, description="Concise description of the ticket")
    key: Optional[str] = Field(None, description="Unique key identifier for the ticket")
    assignees: Optional[List[User]] = Field(None, description="Users assigned to work on the ticket")
    target_url: Optional[str] = Field(None, alias="targetUrl", description="API endpoint URL for accessing the ticket")
    change_log: Optional[ChangeLog] = Field(None, alias="changeLog", description="Audit trail of ticket changes")

class TicketResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the ticket")
    type: str = Field(..., description="Type of ticket")
    name: str = Field(..., description="Short summary or title of the ticket")
    description: Optional[str] = Field(None, description="Concise description of the ticket's purpose and key requirements")
    key: Optional[str] = Field(None, description="Unique key identifier for the ticket in the source system")
    assignees: Optional[List[User]] = Field(None, description="Users assigned to work on the ticket")
    status: TicketStatus = Field(..., description="Current state of the ticket")
    target_url: Optional[str] = Field(None, alias="targetUrl", description="API endpoint URL for accessing the ticket's details")
    change_log: Optional[ChangeLog] = Field(None, alias="changeLog", description="Audit trail of ticket changes")

class TicketsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[TicketSummary] = Field(..., description="List of tickets")

# ---------- COMMENT MODELS ----------
class CommentRequest(BaseModel):
    content: str = Field(..., description="The text content of the comment")
    author_id: Optional[str] = Field(None, alias="authorId", description="ID of the user creating the comment")
    is_internal: Optional[bool] = Field(False, alias="isInternal", description="Whether this comment is internal to the team or visible to external stakeholders")
    mentions: Optional[List[str]] = Field(None, description="IDs of users mentioned in the comment")
    attachment_ids: Optional[List[str]] = Field(None, alias="attachmentIds", description="IDs of attachments associated with the comment")

class CommentResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the comment")
    content: str = Field(..., description="The text content of the comment")
    author: Optional[User] = Field(None, description="User who created the comment")
    is_internal: Optional[bool] = Field(None, alias="isInternal", description="Whether this comment is internal to the team")
    mentions: Optional[List[User]] = Field(None, description="Users mentioned in the comment")
    attachments: Optional[List['AttachmentResponse']] = Field(None, description="Attachments associated with the comment")
    change_log: Optional[ChangeLog] = Field(None, alias="changeLog", description="Audit trail of comment changes")

class CommentsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[CommentResponse] = Field(..., description="List of comments")

# ---------- ATTACHMENT MODELS ----------
class AttachmentRequest(BaseModel):
    file_name: str = Field(..., alias="fileName", description="Name of the file being attached")
    file_size: int = Field(..., alias="fileSize", description="Size of the file in bytes")
    mime_type: str = Field(..., alias="mimeType", description="MIME type of the file")
    description: Optional[str] = Field(None, description="Optional description of the attachment")
    uploaded_by_id: Optional[str] = Field(None, alias="uploadedById", description="ID of the user uploading the attachment")
    is_public: Optional[bool] = Field(True, alias="isPublic", description="Whether the attachment is publicly accessible")

class AttachmentResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the attachment")
    file_name: str = Field(..., alias="fileName", description="Name of the attached file")
    file_size: int = Field(..., alias="fileSize", description="Size of the file in bytes")
    mime_type: str = Field(..., alias="mimeType", description="MIME type of the file")
    description: Optional[str] = Field(None, description="Description of the attachment")
    download_url: Optional[str] = Field(None, alias="downloadUrl", description="URL to download the attachment")
    uploaded_by: Optional[User] = Field(None, alias="uploadedBy", description="User who uploaded the attachment")
    is_public: Optional[bool] = Field(None, alias="isPublic", description="Whether the attachment is publicly accessible")
    change_log: Optional[ChangeLog] = Field(None, alias="changeLog", description="Audit trail of attachment changes")

class AttachmentsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[AttachmentResponse] = Field(..., description="List of attachments")

# ---------- LABEL MODELS ----------
class LabelCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the label")
    description: Optional[str] = Field(None, description="Description of what the label represents")
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code for the label")
    category: Optional[str] = Field(None, description="Category grouping for the label")

class LabelResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the label")
    name: str = Field(..., description="Name of the label")
    description: Optional[str] = Field(None, description="Description of what the label represents")
    color: Optional[str] = Field(None, description="Hex color code for the label")
    category: Optional[str] = Field(None, description="Category grouping for the label")
    usage_count: Optional[int] = Field(None, alias="usageCount", description="Number of tickets using this label")
    change_log: Optional[ChangeLog] = Field(None, alias="changeLog", description="Audit trail of label changes")

class LabelsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[LabelResponse] = Field(..., description="List of labels")

# ---------- SERVICE MODELS ----------
class Connector(BaseModel):
    name: str

class Integration(BaseModel):
    id: str
    name: str

class APIResponse(BaseModel):
    status: str
    message: str
    timestamp: float = Field(default_factory=time.time)
    data: Optional[Any] = None
    error_details: Optional[Any] = None

# Fix forward reference for CommentResponse
CommentResponse.model_rebuild()