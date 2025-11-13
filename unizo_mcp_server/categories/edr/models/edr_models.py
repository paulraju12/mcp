import time
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


# ---------- ENUMS ----------
class DeviceState(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class DeviceAlertState(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class PlatformType(str, Enum):
    ENDPOINT = "ENDPOINT"
    SERVER = "SERVER"
    MOBILE = "MOBILE"
    IOT = "IOT"


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    NEW = "NEW"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    CLOSED = "CLOSED"


# ---------- CORE MODELS ----------
class Pagination(BaseModel):
    total: Optional[int] = Field(None, description="Total number of elements", ge=0)
    limit: Optional[int] = Field(None, description="Page size", ge=1, le=100)
    offset: Optional[int] = Field(None, description="Starting position", ge=0)
    previous: Optional[int] = Field(None, description="Previous page offset", ge=0)
    next: Optional[int] = Field(None, description="Next page offset", ge=0)


class ResponseMetadata(BaseModel):
    requestId: Optional[str] = Field(None, description="Unique request identifier")
    timestamp: Optional[str] = Field(None, description="Response timestamp")
    version: Optional[str] = Field(None, description="API version")
    processingTime: Optional[int] = Field(None, description="Processing time in milliseconds")


class ErrorDetail(BaseModel):
    property: Optional[str] = Field(None, description="Property causing the error")
    reason: Optional[str] = Field(None, description="Reason for the error")


class Error(BaseModel):
    errorCode: Optional[str] = Field(None, pattern="^AP-\\d{7}$", description="Error code")
    errorMessage: Optional[str] = Field(None, description="Error message")
    statusCode: Optional[int] = Field(None, description="HTTP status code")
    correlationId: Optional[str] = Field(None, description="Correlation ID")
    details: Optional[str] = Field(None, description="Additional error details")
    property: Optional[str] = Field(None, description="Property causing validation error")
    help: Optional[str] = Field(None, description="Help information")
    additionalInfo: Optional[List[ErrorDetail]] = Field(None, description="Additional error information")


class ErrorList(BaseModel):
    errors: List[Error] = Field(..., description="List of errors")


# ---------- USER AND CHANGE LOG MODELS ----------
class User(BaseModel):
    href: Optional[str] = Field(None, description="User API URL", format="uri")
    id: Optional[str] = Field(None, description="User ID", format="uuid")
    firstName: Optional[str] = Field(None, description="First name", example="John")
    lastName: Optional[str] = Field(None, description="Last name", example="Doe")
    avatar: Optional[Dict[str, str]] = Field(None, description="Avatar URLs")


class ChangeLog(BaseModel):
    createdDateTime: Optional[str] = Field(None, description="Creation timestamp", format="date-time")
    lastUpdatedDateTime: Optional[str] = Field(None, description="Last update timestamp", format="date-time")
    createdBy: Optional[User] = Field(None, description="User who created")
    lastUpdatedBy: Optional[User] = Field(None, description="User who last updated")


# ---------- PLATFORM AND OS MODELS ----------
class Platform(BaseModel):
    href: Optional[str] = Field(None, description="Platform API URL",
                                example="https://api.unizo.ai/api/v1/platforms/windows-10")
    type: Optional[str] = Field(None, description="Platform type", example="ENDPOINT")
    id: Optional[str] = Field(None, description="Platform ID", example="WIN-10-ENT-x64")
    name: Optional[str] = Field(None, description="Platform name", example="Windows 10 Enterprise")


class OSInfo(BaseModel):
    version: Optional[str] = Field(None, description="OS version", example="10.0.19045")
    major: Optional[str] = Field(None, description="Major version", example="10")
    minor: Optional[str] = Field(None, description="Minor version", example="0")


# ---------- AGENT AND POLICY MODELS ----------
class Policy(BaseModel):
    name: Optional[str] = Field(None, description="Policy name", example="Corporate Endpoint Protection Policy")
    id: Optional[str] = Field(None, description="Policy ID", example="POL-EPP-001")


class AgentInfo(BaseModel):
    agentVersion: Optional[str] = Field(None, description="Agent version", example="7.15.16806.0")
    signatureVersion: Optional[str] = Field(None, description="Signature version", example="2024.06.04.001")
    policies: Optional[List[Policy]] = Field(None, description="Applied policies")


class SourceVendor(BaseModel):
    vendor: Optional[str] = Field(None, description="Vendor name", example="CrowdStrike")
    vendorId: Optional[str] = Field(None, description="Vendor ID", example="CS-FALCON-SENSOR-001")
    agentInfo: Optional[AgentInfo] = Field(None, description="Agent information")


# ---------- INFRASTRUCTURE MODELS ----------
class ADInfo(BaseModel):
    orgUnit: Optional[str] = Field(None, description="Organizational unit",
                                   example="OU=Workstations,OU=IT,DC=corp,DC=example,DC=com")
    siteName: Optional[str] = Field(None, description="Site name", example="Corporate-HQ-Site")
    domain: Optional[str] = Field(None, description="Domain", example="CORP.EXAMPLE.COM")
    deviceId: Optional[str] = Field(None, description="Device ID in AD",
                                    example="CN=DESKTOP-ABC123,CN=Computers,DC=corp,DC=example,DC=com")


class CloudMetadata(BaseModel):
    cloudProvider: Optional[str] = Field(None, description="Cloud provider", example="AWS")
    accountId: Optional[str] = Field(None, description="Account ID", example="123456789012")
    region: Optional[str] = Field(None, description="Region", example="us-east-1")
    availabilityZone: Optional[str] = Field(None, description="Availability zone", example="us-east-1a")
    instanceId: Optional[str] = Field(None, description="Instance ID", example="i-0abcd1234efgh5678")
    instanceType: Optional[str] = Field(None, description="Instance type", example="t3.medium")
    imageId: Optional[str] = Field(None, description="Image ID", example="ami-0123456789abcdef0")
    kernelId: Optional[str] = Field(None, description="Kernel ID", example="aki-0987654321fedcba0")
    vpcId: Optional[str] = Field(None, description="VPC ID", example="vpc-12345678")
    subnetId: Optional[str] = Field(None, description="Subnet ID", example="subnet-abcdef12")


# ---------- DEVICE METADATA MODELS ----------
class DeviceTag(BaseModel):
    key: Optional[str] = Field(None, description="Tag key", example="Department")
    value: Optional[str] = Field(None, description="Tag value", example="IT-Security")
    source: Optional[str] = Field(None, description="Tag source", example="EDR-Agent")


class DeviceIdentity(BaseModel):
    userName: Optional[str] = Field(None, description="Username", example="john.doe@corp.example.com")
    userId: Optional[str] = Field(None, description="User ID", example="S-1-5-21-1234567890-987654321-1122334455-1001")


# ---------- DEVICE MODELS ----------
class DeviceResponse(BaseModel):
    # Core Device Info
    id: Optional[str] = Field(None, description="Device ID", example="DESKTOP-ABC123")
    state: Optional[DeviceState] = Field(None, description="Device state")

    # Platform and OS
    platform: Optional[Platform] = Field(None, description="Platform information")
    os: Optional[OSInfo] = Field(None, description="Operating system information")

    # Network Information
    hostnames: Optional[List[str]] = Field(None, description="Device hostnames",
                                           example=["DESKTOP-ABC123", "workstation-01"])
    fqdns: Optional[List[str]] = Field(None, description="Fully qualified domain names",
                                       example=["desktop-abc123.corp.example.com", "workstation-01.internal.local"])
    ipv4s: Optional[List[str]] = Field(None, description="IPv4 addresses",
                                       example=["192.168.1.100", "10.0.0.25"])
    ipv6s: Optional[List[str]] = Field(None, description="IPv6 addresses",
                                       example=["2001:db8::1", "fe80::1234:5678:9abc:def0"])
    macAddresses: Optional[List[str]] = Field(None, description="MAC addresses",
                                              example=["00:11:22:33:44:55", "AA:BB:CC:DD:EE:FF"])

    # Security and Management
    sourceVendors: Optional[List[SourceVendor]] = Field(None, description="Source vendors and agents")
    installedSoftware: Optional[List[str]] = Field(None, description="Installed software",
                                                   example=["Microsoft Office 365", "Google Chrome", "Slack Desktop"])

    # Infrastructure
    adInfo: Optional[ADInfo] = Field(None, description="Active Directory information")
    cloudMetadata: Optional[CloudMetadata] = Field(None, description="Cloud metadata")

    # Metadata
    tags: Optional[List[DeviceTag]] = Field(None, description="Device tags")
    identities: Optional[List[DeviceIdentity]] = Field(None, description="Device identities")

    # Audit
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class DevicesListResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[DeviceResponse]] = Field(None, description="List of devices")


# ---------- ALERT MODELS ----------
class VendorInfo(BaseModel):
    id: Optional[str] = Field(None, description="Vendor ID", example="CROWDSTRIKE-FALCON")
    severity: Optional[str] = Field(None, description="Vendor-specific severity", example="HIGH")
    status: Optional[str] = Field(None, description="Vendor-specific status")


class DeviceAlertSource(BaseModel):
    system: Optional[str] = Field(None, description="Source system", example="CrowdStrike Falcon EDR")


class DeviceAlertStatus(BaseModel):
    internal: Optional[str] = Field(None, description="Internal status", example="UNDER_INVESTIGATION")
    external: Optional[str] = Field(None, description="External status")


class DeviceAlertResponse(BaseModel):
    # Core Alert Info
    id: Optional[str] = Field(None, description="Alert ID", example="ALT-2024-001-MALWARE")
    state: Optional[DeviceAlertState] = Field(None, description="Alert state")
    title: Optional[str] = Field(None, description="Alert title", example="Suspicious Process Execution Detected")
    description: Optional[str] = Field(None, description="Alert description",example="A potentially malicious process 'powershell.exe' was detected executing suspicious commands")
    severity: Optional[str] = Field(None, description="Alert severity", example="HIGH")

    # Vendor and Source Info
    vendor: Optional[VendorInfo] = Field(None, description="Vendor information")
    source: Optional[DeviceAlertSource] = Field(None, description="Alert source information")
    status: Optional[DeviceAlertStatus] = Field(None, description="Alert status information")

    # Audit
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class DeviceAlertsListResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[DeviceAlertResponse]] = Field(None, description="List of device alerts")


# ---------- COMMON MODELS ----------
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