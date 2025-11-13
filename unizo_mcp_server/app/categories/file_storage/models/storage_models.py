import time
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ---------- CORE MODELS ----------
class Pagination(BaseModel):
    total: Optional[int] = Field(None, description="Total number of elements", ge=1, le=100)
    limit: Optional[int] = Field(None, description="Page size", ge=1, le=100)
    offset: Optional[int] = Field(None, description="Starting position", ge=1, le=100)
    previous: Optional[int] = Field(None, description="Previous page", ge=1, le=100)
    next: Optional[int] = Field(None, description="Next page", ge=1, le=100)


class Avatar(BaseModel):
    original: Optional[str] = Field(None, description="Original avatar URL", format="uri")
    xSmall: Optional[str] = Field(None, description="Extra small avatar URL", format="uri")
    small: Optional[str] = Field(None, description="Small avatar URL", format="uri")
    medium: Optional[str] = Field(None, description="Medium avatar URL", format="uri")
    large: Optional[str] = Field(None, description="Large avatar URL", format="uri")


class User(BaseModel):
    href: Optional[str] = Field(None, description="User API endpoint URL", format="uri")
    id: Optional[str] = Field(None, description="User unique identifier", format="uuid")
    firstName: Optional[str] = Field(None, description="User first name")
    lastName: Optional[str] = Field(None, description="User last name")
    avatar: Optional[Avatar] = Field(None, description="User avatar")


class ChangeLog(BaseModel):
    createdDateTime: Optional[str] = Field(None, description="Creation timestamp", format="date-time")
    lastUpdatedDateTime: Optional[str] = Field(None, description="Last update timestamp", format="date-time")
    createdBy: Optional[User] = Field(None, description="Created by user")
    lastUpdatedBy: Optional[User] = Field(None, description="Last updated by user")


class ErrorDetails(BaseModel):
    errorCode: str = Field(..., description="Error code", pattern=r"^AP-\d{7}$")
    errorMessage: str = Field(..., description="Error message")
    statusCode: int = Field(..., description="HTTP status code")
    correlationId: Optional[str] = Field(None, description="Correlation identifier")
    details: Optional[str] = Field(None, description="Additional error details")
    property: Optional[str] = Field(None, description="Property causing error")
    help: Optional[str] = Field(None, description="Help information")
    additionalInfo: Optional[List[Dict[str, str]]] = Field(None, description="Additional error information")


# ---------- DRIVE MODELS ----------
class DriveResponse(BaseModel):
    name: Optional[str] = Field(None, description="Drive name")
    id: Optional[str] = Field(None, description="Drive ID")
    driveUrl: Optional[str] = Field(None, description="Drive URL", format="uri")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class DrivesResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[DriveResponse]] = Field(None, description="List of drives")


# ---------- FOLDER MODELS ----------
class FolderRequest(BaseModel):
    name: Optional[str] = Field(None, description="Folder name")
    description: Optional[str] = Field(None, description="Folder description")
    size: Optional[str] = Field(None, description="Folder size")
    mimeType: Optional[str] = Field(None, description="MIME type")
    folderUrl: Optional[str] = Field(None, description="Folder URL", format="uri")
    parents: Optional[List[str]] = Field(None, description="Parent folder IDs")


class FolderResponse(BaseModel):
    name: Optional[str] = Field(None, description="Folder name")
    id: Optional[str] = Field(None, description="Folder ID")
    description: Optional[str] = Field(None, description="Folder description")
    size: Optional[str] = Field(None, description="Folder size")
    mimeType: Optional[str] = Field(None, description="MIME type")
    folderUrl: Optional[str] = Field(None, description="Folder URL", format="uri")
    parents: Optional[List[str]] = Field(None, description="Parent folder IDs")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class FoldersResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[FolderResponse]] = Field(None, description="List of folders")


# ---------- FILE MODELS ----------
class FileRequest(BaseModel):
    name: Optional[str] = Field(None, description="File name")
    description: Optional[str] = Field(None, description="File description")
    size: Optional[str] = Field(None, description="File size")
    mimeType: Optional[str] = Field(None, description="MIME type")
    fileUrl: Optional[str] = Field(None, description="File URL", format="uri")
    parents: Optional[List[str]] = Field(None, description="Parent folder IDs")


class FileUpdateRequest(BaseModel):
    content: Optional[str] = Field(None, description="File content")


class FileResponse(BaseModel):
    name: Optional[str] = Field(None, description="File name")
    id: Optional[str] = Field(None, description="File ID")
    description: Optional[str] = Field(None, description="File description")
    size: Optional[str] = Field(None, description="File size")
    mimeType: Optional[str] = Field(None, description="MIME type")
    fileUrl: Optional[str] = Field(None, description="File URL", format="uri")
    parents: Optional[List[str]] = Field(None, description="Parent folder IDs")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class FilesResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[FileResponse]] = Field(None, description="List of files")


# ---------- USER MODELS ----------
class UserResponse(BaseModel):
    name: Optional[str] = Field(None, description="User name")
    id: Optional[str] = Field(None, description="User ID")
    emailAddress: Optional[str] = Field(None, description="Email address")
    status: Optional[str] = Field(None, description="User status")
    isAdmin: Optional[bool] = Field(None, description="Admin status")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class UsersResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[UserResponse]] = Field(None, description="List of users")


# ---------- GROUP MODELS ----------
class GroupResponse(BaseModel):
    name: Optional[str] = Field(None, description="Group name")
    id: Optional[str] = Field(None, description="Group ID")
    description: Optional[str] = Field(None, description="Group description")
    emailAddress: Optional[str] = Field(None, description="Email address")
    membersCount: Optional[int] = Field(None, description="Members count")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class GroupsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[GroupResponse]] = Field(None, description="List of groups")


# ---------- VERSION MODELS (FIXED) ----------
class VersionResponse(BaseModel):
    id: Optional[str] = Field(None, description="Version ID")
    username: Optional[str] = Field(None, description="Username")
    size: Optional[str] = Field(None, description="File size")
    mimeType: Optional[str] = Field(None, description="MIME type")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class VersionsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[VersionResponse]] = Field(None, description="List of versions")


# ---------- PERMISSION MODELS (FIXED) ----------
class PermissionRequest(BaseModel):
    userRole: Optional[str] = Field(None, description="User role")
    userType: Optional[str] = Field(None, description="User type")
    emailAddress: Optional[str] = Field(None, description="Email address")


class PermissionResponse(BaseModel):
    id: Optional[str] = Field(None, description="Permission ID")
    userRole: Optional[str] = Field(None, description="User role")
    userType: Optional[str] = Field(None, description="User type")
    emailAddress: Optional[str] = Field(None, description="Email address")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class PermissionsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[PermissionResponse]] = Field(None, description="List of permissions")


# ---------- COMMENT MODELS ----------
class CommentRequest(BaseModel):
    content: Optional[str] = Field(None, description="Comment content")
    username: Optional[str] = Field(None, description="Username")


class CommentResponse(BaseModel):
    id: Optional[str] = Field(None, description="Comment ID")
    content: Optional[str] = Field(None, description="Comment content")
    username: Optional[str] = Field(None, description="Username")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class CommentsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[CommentResponse]] = Field(None, description="List of comments")


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


# Update forward references
User.model_rebuild()
ChangeLog.model_rebuild()