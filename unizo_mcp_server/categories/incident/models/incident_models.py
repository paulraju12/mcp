import time
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ---------- ENUMS ----------
class IncidentStatus(str, Enum):
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    POSTMORTEM = "postmortem"

class IncidentPriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"

class PriorityName(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class IncidentType(str, Enum):
    SERVICE = "service"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    PERFORMANCE = "performance"

class UrgencyType(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"

class TargetType(str, Enum):
    SERVICE = "service"
    INFRASTRUCTURE = "infrastructure"
    DATABASE = "database"
    API = "api"

# ---------- MODELS ----------
class Pagination(BaseModel):
    total: Optional[int] = Field(None, description="Total number of items available")
    limit: Optional[int] = Field(None, description="Maximum number of items per page")
    offset: Optional[int] = Field(None, description="Starting position of the current page")
    previous: Optional[int] = Field(None, description="Starting position of the previous page")
    next: Optional[int] = Field(None, description="Starting position of the next page")

class ChangeLog(BaseModel):
    createdDateTime: Optional[str] = Field(None, description="Timestamp when the resource was created")
    lastUpdatedDateTime: Optional[str] = Field(None, description="Timestamp when the resource was last updated")

class Avatar(BaseModel):
    original: Optional[str] = Field(None, description="Original avatar URL")
    xSmall: Optional[str] = Field(None, description="Extra small avatar URL")
    small: Optional[str] = Field(None, description="Small avatar URL")
    medium: Optional[str] = Field(None, description="Medium avatar URL")
    large: Optional[str] = Field(None, description="Large avatar URL")

class User(BaseModel):
    href: Optional[str] = Field(None, description="API endpoint URL for the user")
    id: str = Field(..., description="Unique identifier for the user")
    firstName: Optional[str] = Field(None, description="User's first name")
    lastName: Optional[str] = Field(None, description="User's last name")
    avatar: Optional[Avatar] = Field(None, description="Avatar URLs in different sizes")

class Organization(BaseModel):
    id: str = Field(..., description="Unique identifier for the organization")
    login: Optional[str] = Field(None, description="Login identifier for the organization")
    name: str = Field(..., description="Name of the organization")
    changeLog: Optional[ChangeLog] = Field(None, description="Audit trail of organization changes")

class OrganizationsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[Organization] = Field(..., description="List of organizations")

class Team(BaseModel):
    href: Optional[str] = Field(None, description="URL of the team")
    type: Optional[str] = Field(None, description="Type of the team")
    id: str = Field(..., description="Unique identifier of the team")
    name: str = Field(..., description="Name of the team")
    description: Optional[str] = Field(None, description="Description of the team")
    url: Optional[str] = Field(None, description="URL of the team")
    changeLog: Optional[ChangeLog] = Field(None, description="Audit trail of team changes")

class TeamsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[Team] = Field(..., description="List of teams")

class Service(BaseModel):
    href: Optional[str] = Field(None, description="URL of the service")
    type: Optional[str] = Field(None, description="Type of the service")
    id: str = Field(..., description="Unique identifier of the service")
    name: str = Field(..., description="Name of the service")
    description: Optional[str] = Field(None, description="Description of the service")
    team: Optional[Team] = Field(None, description="Team responsible for the service")
    url: Optional[str] = Field(None, description="URL of the service")
    changeLog: Optional[ChangeLog] = Field(None, description="Audit trail of service changes")

class ServicesResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[Service] = Field(..., description="List of services")

class Priority(BaseModel):
    type: IncidentPriority = Field(..., description="Type of priority")
    id: str = Field(..., description="Unique identifier of the priority")
    name: PriorityName = Field(..., description="Name of the priority")

class Target(BaseModel):
    type: TargetType = Field(..., description="Type of the target")
    slug: str = Field(..., description="Identifier of the target")

class Project(BaseModel):
    type: Optional[str] = Field(None, description="Type of the project")
    id: str = Field(..., description="Unique identifier of the project")
    name: str = Field(..., description="Name of the project")

class ServiceInfo(BaseModel):
    type: Optional[str] = Field(None, description="Type of the service")
    id: str = Field(..., description="Unique identifier of the service")
    name: str = Field(..., description="Name of the service")

class Incident(BaseModel):
    id: str = Field(..., description="Unique identifier of the incident")
    name: str = Field(..., description="Name of the incident")
    title: Optional[str] = Field(None, description="Title of the incident")
    login: Optional[str] = Field(None, description="Login identifier for the incident")
    status: IncidentStatus = Field(..., description="Current status of the incident")
    priority: Optional[Priority] = Field(None, description="Priority information")
    description: Optional[str] = Field(None, description="Description of the incident")
    incidentKey: Optional[str] = Field(None, description="Unique key for the incident")
    createdBy: Optional[str] = Field(None, description="Creator of the incident")
    url: Optional[str] = Field(None, description="URL of the incident")
    urgency: Optional[UrgencyType] = Field(None, description="Urgency level")
    username: Optional[str] = Field(None, description="Username of the incident creator")
    targets: Optional[List[Target]] = Field(None, description="List of affected targets")
    project: Optional[Project] = Field(None, description="Project information")
    service: Optional[ServiceInfo] = Field(None, description="Primary service information")
    isMultiResponder: Optional[bool] = Field(None, description="Whether multiple responders are assigned")
    team: Optional[Team] = Field(None, description="Primary response team")
    services: Optional[List[Service]] = Field(None, description="List of affected services")
    organization: Optional[Organization] = Field(None, description="Organization information")
    changeLog: Optional[ChangeLog] = Field(None, description="Audit trail of incident changes")

class IncidentsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: List[Incident] = Field(..., description="List of incidents")

class IncidentCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the incident", min_length=5, max_length=100)
    title: str = Field(..., description="Title of the incident", min_length=10, max_length=200)
    description: str = Field(..., description="Description of the incident", min_length=20, max_length=1000)
    status: IncidentStatus = Field(..., description="Current status of the incident")
    username: Optional[str] = Field(None, description="Username of the incident creator")
    type: Optional[IncidentType] = Field(None, description="Type of the incident")
    targets: Optional[List[Target]] = Field(None, description="List of affected targets")
    isMultiResponder: Optional[bool] = Field(None, description="Whether multiple responders are assigned")
    priority: Priority = Field(..., description="Priority information")
    project: Optional[Project] = Field(None, description="Project information")
    service: ServiceInfo = Field(..., description="Primary service information")

class IncidentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Name of the incident", min_length=5, max_length=100)
    title: Optional[str] = Field(None, description="Title of the incident", min_length=10, max_length=200)
    description: Optional[str] = Field(None, description="Description of the incident", min_length=20, max_length=1000)
    status: Optional[IncidentStatus] = Field(None, description="Current status of the incident")
    username: Optional[str] = Field(None, description="Username of the incident creator")
    type: Optional[IncidentType] = Field(None, description="Type of the incident")
    targets: Optional[List[Target]] = Field(None, description="List of affected targets")
    isMultiResponder: Optional[bool] = Field(None, description="Whether multiple responders are assigned")
    priority: Optional[Priority] = Field(None, description="Priority information")
    project: Optional[Project] = Field(None, description="Project information")
    service: Optional[ServiceInfo] = Field(None, description="Primary service information")

class IncidentConnector(BaseModel):
    name: str

class IncidentIntegration(BaseModel):
    id: str
    name: str

class APIResponse(BaseModel):
    status: str
    message: str
    timestamp: float = Field(default_factory=time.time)
    data: Optional[Any] = None
    error_details: Optional[Any] = None