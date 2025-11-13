import time
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


# ---------- ENUMS ----------
class AccountType(str, Enum):
    LOCAL = "Local"
    DOMAIN = "Domain"
    SERVICE = "Service"
    SYSTEM = "System"
    GUEST = "Guest"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"


class UserType(str, Enum):
    USER = "User"
    ADMIN = "Admin"
    SERVICE = "Service"
    SYSTEM = "System"
    GUEST = "Guest"


class MfaStatus(str, Enum):
    ENABLED = "Enabled"
    DISABLED = "Disabled"
    PENDING = "Pending"
    REQUIRED = "Required"


class MfaMethodType(str, Enum):
    SMS = "SMS"
    TOTP = "TOTP"
    WEBAUTHN = "WebAuthn"
    PUSH = "Push"
    BACKUP_CODES = "Backup_Codes"


class GroupType(str, Enum):
    SECURITY = "Security"
    DISTRIBUTION = "Distribution"
    UNIVERSAL = "Universal"
    MAIL_ENABLED = "Mail_Enabled"
    ROLE_BASED = "Role_Based"


class GroupStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    ARCHIVED = "ARCHIVED"


class MemberType(str, Enum):
    USER = "user"
    GROUP = "group"
    SERVICE_PRINCIPAL = "servicePrincipal"


class MemberStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class MembershipType(str, Enum):
    DIRECT = "Direct"
    INHERITED = "Inherited"
    DYNAMIC = "Dynamic"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class AuthenticationMethod(str, Enum):
    PASSWORD = "Password"
    SSO = "SSO"
    CERTIFICATE = "Certificate"
    BIOMETRIC = "Biometric"
    TOKEN = "Token"


class DeviceType(str, Enum):
    DESKTOP = "Desktop"
    LAPTOP = "Laptop"
    MOBILE = "Mobile"
    TABLET = "Tablet"
    SERVER = "Server"
    IOT = "IoT"
    UNKNOWN = "Unknown"


class OSType(str, Enum):
    WINDOWS = "Windows"
    MACOS = "macOS"
    LINUX = "Linux"
    IOS = "iOS"
    ANDROID = "Android"
    OTHER = "Other"


class NetworkStatus(str, Enum):
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    VPN = "VPN"
    QUARANTINED = "Quarantined"


class IdpType(str, Enum):
    SAML = "SAML"
    OIDC = "OIDC"
    LDAP = "LDAP"
    LOCAL = "Local"


class Protocol(str, Enum):
    SSH = "SSH"
    RDP = "RDP"
    HTTPS = "HTTPS"
    VNC = "VNC"


# ---------- CORE MODELS ----------
class Pagination(BaseModel):
    total: Optional[int] = Field(None, description="Total number of elements")
    limit: Optional[int] = Field(None, description="Page size")
    offset: Optional[int] = Field(None, description="Starting position")
    previous: Optional[str] = Field(None, description="Previous page URL")
    next: Optional[str] = Field(None, description="Next page URL")
    pages: Optional[int] = Field(None, description="Total number of pages")


class ResponseMetadata(BaseModel):
    requestId: Optional[str] = Field(None, description="Unique request identifier")
    timestamp: Optional[str] = Field(None, description="Response timestamp")
    version: Optional[str] = Field(None, description="API version")
    processingTime: Optional[int] = Field(None, description="Processing time in milliseconds")


class ErrorResponse(BaseModel):
    errorCode: str = Field(..., description="Error code")
    errorMessage: str = Field(..., description="Error message")
    statusCode: int = Field(..., description="HTTP status code")
    correlationId: Optional[str] = Field(None, description="Correlation ID")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: Optional[str] = Field(None, description="Error timestamp")
    path: Optional[str] = Field(None, description="Request path")


# ---------- USER MODELS ----------
class Account(BaseModel):
    name: str = Field(..., description="Account name")
    type: AccountType = Field(..., description="Account type")
    typeId: Optional[int] = Field(None, description="Numeric identifier for account type")
    uid: str = Field(..., description="Account unique identifier")
    labels: Optional[List[str]] = Field(None, description="Account labels for categorization")


class MfaMethod(BaseModel):
    type: MfaMethodType = Field(..., description="MFA method type")
    isDefault: bool = Field(..., description="Whether this is the default method")
    isVerified: Optional[bool] = Field(None, description="Whether method is verified")
    lastUsed: Optional[str] = Field(None, description="Last used timestamp")
    phoneNumber: Optional[str] = Field(None, description="Phone number for SMS method")
    deviceName: Optional[str] = Field(None, description="Device name for WebAuthn")


class UserReference(BaseModel):
    id: str = Field(..., description="User ID")
    uid: Optional[str] = Field(None, description="Alternative identifier")
    username: Optional[str] = Field(None, description="Username")
    firstName: Optional[str] = Field(None, description="First name")
    lastName: Optional[str] = Field(None, description="Last name")
    email: Optional[str] = Field(None, description="Email address")
    href: Optional[str] = Field(None, description="API endpoint URL")


class LdapPerson(BaseModel):
    ldapDn: Optional[str] = Field(None, description="LDAP Distinguished Name")
    ldapCn: Optional[str] = Field(None, description="LDAP Common Name")
    employeeUid: Optional[str] = Field(None, description="Employee identifier")
    givenName: Optional[str] = Field(None, description="Given name")
    surname: Optional[str] = Field(None, description="Surname")
    mail: Optional[str] = Field(None, description="Email address")
    title: Optional[str] = Field(None, description="Job title")
    department: Optional[str] = Field(None, description="Department")
    company: Optional[str] = Field(None, description="Company name")
    telephoneNumber: Optional[str] = Field(None, description="Telephone number")


class GroupSummary(BaseModel):
    id: str = Field(..., description="Group identifier")
    uid: Optional[str] = Field(None, description="Group UID")
    name: str = Field(..., description="Group name")
    displayName: Optional[str] = Field(None, description="Group display name")
    type: Optional[GroupType] = Field(None, description="Group type")
    href: Optional[str] = Field(None, description="API endpoint URL")


class OrgInfo(BaseModel):
    name: Optional[str] = Field(None, description="Organization name")
    unit: Optional[str] = Field(None, description="Organizational unit")
    division: Optional[str] = Field(None, description="Division")
    costCenter: Optional[str] = Field(None, description="Cost center")


class Location(BaseModel):
    country: Optional[str] = Field(None, description="Country")
    state: Optional[str] = Field(None, description="State or province")
    city: Optional[str] = Field(None, description="City")
    address: Optional[str] = Field(None, description="Street address")
    postalCode: Optional[str] = Field(None, description="Postal code")


class OSInfo(BaseModel):
    name: Optional[str] = Field(None, description="OS name")
    version: Optional[str] = Field(None, description="OS version")
    build: Optional[str] = Field(None, description="OS build number")
    type: Optional[OSType] = Field(None, description="OS type")


class Device(BaseModel):
    id: str = Field(..., description="Device identifier")
    name: str = Field(..., description="Device name")
    type: DeviceType = Field(..., description="Device type")
    os: Optional[OSInfo] = Field(None, description="Operating system")
    isManaged: bool = Field(..., description="Whether device is managed")
    isCompliant: bool = Field(..., description="Whether device is compliant")
    lastSeen: Optional[str] = Field(None, description="Last seen timestamp")
    networkStatus: Optional[NetworkStatus] = Field(None, description="Network status")


class Authorization(BaseModel):
    resource: str = Field(..., description="Resource being accessed")
    action: str = Field(..., description="Action being performed")
    decision: str = Field(..., description="Authorization decision (Allow/Deny)")
    timestamp: str = Field(..., description="Authorization timestamp")


class IdpInfo(BaseModel):
    type: IdpType = Field(..., description="Identity provider type")
    name: str = Field(..., description="Identity provider name")
    realm: Optional[str] = Field(None, description="Authentication realm")


# ---------- GROUP MODELS ----------
class GroupReference(BaseModel):
    id: str = Field(..., description="Group ID")
    uid: Optional[str] = Field(None, description="Alternative identifier")
    name: str = Field(..., description="Group name")
    displayName: Optional[str] = Field(None, description="Display name")
    type: Optional[GroupType] = Field(None, description="Group type")
    href: Optional[str] = Field(None, description="API endpoint URL")


class GroupResponse(BaseModel):
    # Core Identity
    id: str = Field(..., description="Group unique identifier")
    uid: Optional[str] = Field(None, description="Alternative identifier")
    name: str = Field(..., description="Group name")
    displayName: Optional[str] = Field(None, description="Display name")
    description: Optional[str] = Field(None, description="Group description")

    # Type and Status
    type: GroupType = Field(..., description="Group type")
    status: GroupStatus = Field(..., description="Group status")

    # Organization
    domain: Optional[str] = Field(None, description="Domain")
    org: Optional[OrgInfo] = Field(None, description="Organization information")

    # Membership
    memberCount: Optional[int] = Field(None, description="Number of members")
    members: Optional[List[GroupReference]] = Field(None, description="Group members (when expanded)")

    # Hierarchy
    parentGroups: Optional[List[GroupReference]] = Field(None, description="Parent groups")
    childGroups: Optional[List[GroupReference]] = Field(None, description="Child groups")

    # Privileges
    privileges: Optional[List[str]] = Field(None, description="Group privileges")

    # Audit Information
    createdAt: str = Field(..., description="Creation timestamp")
    updatedAt: Optional[str] = Field(None, description="Last update timestamp")
    createdBy: Optional[UserReference] = Field(None, description="Creator")
    lastUpdatedBy: Optional[UserReference] = Field(None, description="Last updater")


class GroupsListResponse(BaseModel):
    data: List[GroupResponse] = Field(..., description="List of groups")
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    metadata: Optional[ResponseMetadata] = Field(None, description="Response metadata")


# ---------- GROUP MEMBER MODELS ----------
class ServicePrincipal(BaseModel):
    id: str = Field(..., description="Service principal ID")
    name: str = Field(..., description="Service principal name")
    appId: Optional[str] = Field(None, description="Application ID")
    description: Optional[str] = Field(None, description="Description")


class GroupMemberResponse(BaseModel):
    id: str = Field(..., description="Member identifier")
    type: MemberType = Field(..., description="Type of member")
    status: MemberStatus = Field(..., description="Member status in group")
    joinedAt: str = Field(..., description="When member joined the group")
    expiresAt: Optional[str] = Field(None, description="When membership expires")
    addedBy: Optional[UserReference] = Field(None, description="User who added member")

    # Member details based on type
    user: Optional[UserReference] = Field(None, description="User details if member is user")
    group: Optional[GroupReference] = Field(None, description="Group details if member is group")
    servicePrincipal: Optional[ServicePrincipal] = Field(None, description="Service principal details")

    # Membership metadata
    membershipType: Optional[MembershipType] = Field(None, description="How membership was established")
    inheritedFrom: Optional[GroupReference] = Field(None, description="Group from which membership is inherited")
    privileges: Optional[List[str]] = Field(None, description="Specific privileges within this group")


class GroupMembersListResponse(BaseModel):
    data: List[GroupMemberResponse] = Field(..., description="List of group members")
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    metadata: Optional[ResponseMetadata] = Field(None, description="Response metadata")


# ---------- SESSION MODELS ----------
class SessionDevice(BaseModel):
    uid: Optional[str] = Field(None, description="Device unique identifier")
    hostname: Optional[str] = Field(None, description="Device hostname")
    ip: Optional[str] = Field(None, description="Device IP address")
    mac: Optional[str] = Field(None, description="MAC address")
    userAgent: Optional[str] = Field(None, description="User agent string")
    os: Optional[OSInfo] = Field(None, description="Operating system information")
    browser: Optional[Dict[str, str]] = Field(None, description="Browser information")


class SessionLocation(BaseModel):
    ip: Optional[str] = Field(None, description="IP address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    country: Optional[str] = Field(None, description="Country")
    countryCode: Optional[str] = Field(None, description="Country code")
    lat: Optional[float] = Field(None, description="Latitude")
    long: Optional[float] = Field(None, description="Longitude")
    isp: Optional[str] = Field(None, description="Internet service provider")
    org: Optional[str] = Field(None, description="Organization")
    isTrustedLocation: Optional[bool] = Field(None, description="Whether location is trusted")


class SessionResponse(BaseModel):
    # Core Session Info
    uid: str = Field(..., description="Session unique identifier")
    uuid: Optional[str] = Field(None, description="Session UUID")
    userId: str = Field(..., description="User ID associated with session")

    # Authentication
    isMfa: bool = Field(..., description="Whether session was authenticated with MFA")
    mfaMethod: Optional[MfaMethodType] = Field(None, description="MFA method used")
    authenticationMethod: Optional[AuthenticationMethod] = Field(None, description="Authentication method")

    # Session Properties
    isRemote: Optional[bool] = Field(None, description="Whether session is remote")
    isVpn: Optional[bool] = Field(None, description="Whether session is over VPN")

    # Timestamps
    createdTime: Optional[int] = Field(None, description="Unix timestamp of creation")
    createdTimeDt: str = Field(..., description="Session creation datetime")
    expirationTime: Optional[int] = Field(None, description="Unix timestamp of expiration")
    expirationTimeDt: Optional[str] = Field(None, description="Session expiration datetime")
    lastActivityTime: Optional[str] = Field(None, description="Last activity timestamp")

    # Status
    expirationReason: Optional[str] = Field(None, description="Reason for session expiration")
    status: SessionStatus = Field(..., description="Current session status")

    # Context
    terminal: Optional[str] = Field(None, description="Terminal or device identifier")
    issuer: Optional[str] = Field(None, description="Session issuer")
    credentialUid: Optional[str] = Field(None, description="Credential used for authentication")
    count: Optional[int] = Field(None, description="Number of authentication attempts")

    # Device and Location
    device: Optional[SessionDevice] = Field(None, description="Device information")
    location: Optional[SessionLocation] = Field(None, description="Location information")

    # Additional Data
    protocol: Optional[Protocol] = Field(None, description="Protocol used")
    application: Optional[str] = Field(None, description="Application or service accessed")
    sessionFlags: Optional[List[str]] = Field(None, description="Session flags")


class SessionsListResponse(BaseModel):
    data: List[SessionResponse] = Field(..., description="List of sessions")
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    metadata: Optional[ResponseMetadata] = Field(None, description="Response metadata")


# ---------- AUDIT LOG MODELS ----------
class AuditLogResponse(BaseModel):
    id: str = Field(..., description="Audit log unique identifier")
    userId: Optional[str] = Field(None, description="User ID who performed the action")
    userEmail: Optional[str] = Field(None, description="Email of user who performed the action")
    userType: Optional[str] = Field(None, description="Type of user who performed the action")
    eventPublished: Optional[str] = Field(None, description="When the event was published")
    eventType: Optional[str] = Field(None, description="Type of event")
    eventName: Optional[str] = Field(None, description="Name of the event")


class AuditLogsListResponse(BaseModel):
    data: List[AuditLogResponse] = Field(..., description="List of audit logs")
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    metadata: Optional[ResponseMetadata] = Field(None, description="Response metadata")


# ---------- USER MODEL ----------
class UserResponse(BaseModel):
    # Core Identity
    id: str = Field(..., description="Unique identifier of the user")
    uidAlt: Optional[str] = Field(None, description="Alternative unique identifier")
    username: str = Field(..., description="Username for authentication")
    email: str = Field(..., description="Primary email address")

    # Account Information
    account: Account = Field(..., description="Account information")

    # Personal Information
    firstName: Optional[str] = Field(None, description="User's first name")
    lastName: Optional[str] = Field(None, description="User's last name")
    fullName: Optional[str] = Field(None, description="User's full display name")

    # Domain and Authentication
    domain: Optional[str] = Field(None, description="User's authentication domain")
    credentialUid: Optional[str] = Field(None, description="Unique identifier for user credentials")

    # Multi-Factor Authentication
    mfaStatus: MfaStatus = Field(..., description="Current MFA status")
    mfaStatusId: Optional[int] = Field(None, description="Numeric identifier for MFA status")
    hasMfa: Optional[bool] = Field(None, description="Whether user has MFA configured")
    mfaMethods: Optional[List[MfaMethod]] = Field(None, description="Available MFA methods")

    # LDAP/Directory Information
    ldapPerson: Optional[LdapPerson] = Field(None, description="LDAP person information")

    # Groups and Privileges
    groups: Optional[List[GroupSummary]] = Field(None, description="Groups the user belongs to")
    privileges: Optional[List[str]] = Field(None, description="Direct privileges assigned to user")

    # Organization Information
    org: Optional[OrgInfo] = Field(None, description="Organization information")

    # User Status
    userStatus: Optional[str] = Field(None, description="Current user account status")
    userStatusId: Optional[int] = Field(None, description="Numeric identifier for user status")
    status: UserStatus = Field(..., description="Overall account status")

    # Location and Devices
    location: Optional[Location] = Field(None, description="User location information")
    devices: Optional[List[Device]] = Field(None, description="Devices associated with the user")

    # Authorizations
    authorizations: Optional[List[Authorization]] = Field(None, description="Authorization decisions")

    # Identity Provider
    idp: Optional[IdpInfo] = Field(None, description="Identity provider information")

    # Additional Metadata
    labels: Optional[List[str]] = Field(None, description="User labels for categorization")
    type: UserType = Field(..., description="User type classification")
    typeId: Optional[int] = Field(None, description="Numeric identifier for user type")

    # Audit Information
    createdAt: str = Field(..., description="When the user was created")
    updatedAt: Optional[str] = Field(None, description="When the user was last updated")
    createdBy: Optional[UserReference] = Field(None, description="User who created this user")
    lastUpdatedBy: Optional[UserReference] = Field(None, description="User who last updated this user")


class UsersListResponse(BaseModel):
    data: List[UserResponse] = Field(..., description="List of users")
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    metadata: Optional[ResponseMetadata] = Field(None, description="Response metadata")


class Service(BaseModel):
    name: str

# Alias for backward compatibility
Connector = Service

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