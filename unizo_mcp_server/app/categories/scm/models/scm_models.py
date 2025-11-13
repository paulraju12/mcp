import time
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ---------- ENUMS ----------
class DownloadType(str, Enum):
    ONE_STEP_DOWNLOAD = "ONE_STEP_DOWNLOAD"
    TWO_STEPS_DOWNLOAD = "TWO_STEPS_DOWNLOAD"
    THREE_STEPS_DOWNLOAD = "THREE_STEPS_DOWNLOAD"

class PullRequestState(str, Enum):
    OPENED = "opened"
    CLOSED = "closed"
    MERGED = "merged"

class PullRequestVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"

# ---------- BASE MODELS ----------
class Pagination(BaseModel):
    total: Optional[int] = Field(None, description="Total number of elements in the result set", ge=0)
    limit: Optional[int] = Field(None, description="Maximum number of items to return per page", ge=1, le=100)
    offset: Optional[int] = Field(None, description="Starting position for pagination (0-based index)", ge=0)
    previous: Optional[int] = Field(None, description="Offset for the previous page, null if on first page")
    next: Optional[int] = Field(None, description="Offset for the next page, null if on last page")

class ChangeLog(BaseModel):
    createdDateTime: Optional[str] = Field(None, description="Timestamp when the resource was created")
    lastUpdatedDateTime: Optional[str] = Field(None, description="Timestamp when the resource was last updated")

class Download(BaseModel):
    url: str = Field(..., description="URL for downloading content")
    type: DownloadType = Field(..., description="Type of download process required")

class Avatar(BaseModel):
    original: Optional[str] = Field(None, description="Original high-resolution avatar image")
    xSmall: Optional[str] = Field(None, description="Extra small avatar image (32x32 pixels)")
    small: Optional[str] = Field(None, description="Small avatar image (64x64 pixels)")
    medium: Optional[str] = Field(None, description="Medium avatar image (128x128 pixels)")
    large: Optional[str] = Field(None, description="Large avatar image (256x256 pixels)")

class User(BaseModel):
    href: Optional[str] = Field(None, description="API endpoint URL for the user")
    id: str = Field(..., description="Unique identifier for the user")
    firstName: Optional[str] = Field(None, description="User's first name")
    lastName: Optional[str] = Field(None, description="User's last name")
    avatar: Optional[Avatar] = Field(None, description="Avatar URLs in different sizes for responsive display")

# ---------- ORGANIZATION MODELS ----------
class Organization(BaseModel):
    id: str = Field(..., description="Unique identifier for the SCM organization", example="Acme-Inc")
    type: Optional[str] = Field(None, description="Type of SCM organization (e.g., GitHub, GitLab, Bitbucket)", example="Organization")
    description: Optional[str] = Field(None, description="Detailed description of the SCM organization's purpose and scope")
    login: Optional[str] = Field(None, description="Organization's login name in the SCM system")
    url: Optional[str] = Field(None, description="API endpoint URL for the SCM organization")
    twoFactorRequirementEnabled: Optional[bool] = Field(None, description="Whether two-factor authentication is required for organization members")
    membersCanCreatePublicRepositories: Optional[bool] = Field(None, description="Whether organization members are allowed to create public repositories")
    avatarUrl: Optional[str] = Field(None, description="URL to the organization's avatar in the SCM system")
    createdAt: Optional[str] = Field(None, description="Timestamp when the organization was created in the SCM system")
    updatedAt: Optional[str] = Field(None, description="Timestamp when the organization was last updated in the SCM system")

class OrganizationsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination metadata for handling large result sets")
    data: List[Organization] = Field(..., description="Paginated list of source control management organizations")

# ---------- REPOSITORY MODELS ----------
class Repository(BaseModel):
    id: str = Field(..., description="Unique identifier for the source code repository")
    description: Optional[str] = Field(None, description="Detailed description of the repository's purpose and contents")
    fullName: Optional[str] = Field(None, description="Full repository name including organization prefix")
    language: Optional[str] = Field(None, description="Primary programming language used in the repository")
    download: Optional[Download] = Field(None, description="Repository download configuration and options")
    size: Optional[str] = Field(None, description="Size of the repository in bytes")
    private: Optional[bool] = Field(None, description="Whether the repository is private or public")
    archived: Optional[bool] = Field(None, description="Whether the repository is archived and read-only")
    organization: Optional[str] = Field(None, description="Name of the organization that owns the repository")
    url: Optional[str] = Field(None, description="API endpoint URL for the repository")
    defaultBranch: Optional[str] = Field(None, description="Name of the default branch for the repository")
    createdAt: Optional[str] = Field(None, description="Timestamp when the repository was created")
    updatedAt: Optional[str] = Field(None, description="Timestamp when the repository was last updated")
    changeLog: Optional[ChangeLog] = Field(None, description="Audit trail of resource creation and modifications")

class RepositoriesResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination metadata for handling large result sets")
    data: List[Repository] = Field(..., description="Paginated list of source code repositories within an organization")

# ---------- BRANCH MODELS ----------
class Branch(BaseModel):
    name: str = Field(..., description="Branch name", example="main")
    sha: Optional[str] = Field(None, description="Commit SHA of the branch's latest commit")
    url: Optional[str] = Field(None, description="API URL for the branch's latest commit")
    download: Optional[Download] = Field(None, description="Download information for the branch")
    enabled: Optional[bool] = Field(None, description="Whether the branch is enabled")
    authorName: Optional[str] = Field(None, description="Name of the commit author")
    authorDate: Optional[str] = Field(None, description="Timestamp of the author's commit")
    committerName: Optional[str] = Field(None, description="Name of the commit committer")
    committerDate: Optional[str] = Field(None, description="Timestamp of the committer's commit")

class BranchesResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination metadata for handling large result sets")
    data: List[Branch] = Field(..., description="List of branches in the repository")

# ---------- COMMIT MODELS ----------
class CommitParent(BaseModel):
    sha: str = Field(..., description="SHA of the parent commit")
    url: Optional[str] = Field(None, description="API URL for the parent commit")
    htmlUrl: Optional[str] = Field(None, description="HTML URL for the parent commit")

class Commit(BaseModel):
    id: str = Field(..., description="Unique identifier (SHA) for the commit")
    url: Optional[str] = Field(None, description="API endpoint URL for accessing the commit details")
    sha: str = Field(..., description="Git commit SHA (Secure Hash Algorithm)")
    author: Optional[str] = Field(None, description="Username of the commit author")
    parents: Optional[List[CommitParent]] = Field(None, description="List of parent commit references")

class CommitsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination metadata for handling large result sets")
    data: List[Commit] = Field(..., description="List of commits in the repository")

# ---------- PULL REQUEST MODELS ----------
class PullRequest(BaseModel):
    id: str = Field(..., description="Unique identifier for the pull request")
    name: Optional[str] = Field(None, description="Full pull request name including organization and repository")
    title: Optional[str] = Field(None, description="Title of the pull request")
    description: Optional[str] = Field(None, description="Detailed description of the changes in the pull request")
    state: Optional[PullRequestState] = Field(None, description="Current state of the pull request")
    nodeId: Optional[str] = Field(None, description="Unique node identifier in the SCM system")
    htmlUrl: Optional[str] = Field(None, description="Web interface URL for viewing the pull request")
    creator: Optional[str] = Field(None, description="Identifier of the user who created the pull request")
    count: Optional[int] = Field(None, description="Number of commits included in the pull request")
    visibility: Optional[PullRequestVisibility] = Field(None, description="Visibility level of the pull request")

class PullRequestsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination metadata for handling large result sets")
    data: List[PullRequest] = Field(..., description="Paginated list of pull requests in a repository")

class PullRequestRequest(BaseModel):
    title: str = Field(..., description="Title of the pull request")
    description: Optional[str] = Field(None, description="Detailed description of the changes to be merged")
    source: str = Field(..., description="Source branch containing the changes")
    target: str = Field(..., description="Target branch to merge changes into")
    state: Optional[PullRequestState] = Field(PullRequestState.OPENED, description="Initial state of the pull request")
    visibility: Optional[PullRequestVisibility] = Field(PullRequestVisibility.PRIVATE, description="Visibility level for the pull request")

# ---------- ERROR MODELS ----------
class Error(BaseModel):
    code: Optional[str] = Field(None, description="Error code")
    message: Optional[str] = Field(None, description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")

class ErrorList(BaseModel):
    errors: List[Error] = Field(..., description="List of errors")


class Connector(BaseModel):
    name: str

class Integration(BaseModel):
    id: str
    name: str

# ---------- API RESPONSE MODELS ----------
class APIResponse(BaseModel):
    status: str
    message: str
    timestamp: float = Field(default_factory=time.time)
    data: Optional[Any] = None
    error_details: Optional[Any] = None