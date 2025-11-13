import time
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


# ---------- ENUMS ----------
class VulnerabilitySeverity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


class VulnerabilityState(str, Enum):
    OPEN = "Open"
    CONFIRMED = "Confirmed"
    IN_PROGRESS = "In Progress"
    FIXED = "Fixed"
    FALSE_POSITIVE = "False Positive"
    RISK_ACCEPTED = "Risk Accepted"
    CLOSED = "Closed"


class AssetType(str, Enum):
    SERVER = "Server"
    WORKSTATION = "Workstation"
    MOBILE = "Mobile"
    NETWORK_DEVICE = "Network Device"
    IOT_DEVICE = "IoT Device"
    CLOUD_INSTANCE = "Cloud Instance"
    CONTAINER = "Container"
    WEB_APPLICATION = "Web Application"


class ScanStatus(str, Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    PAUSED = "Paused"


class ScanType(str, Enum):
    VULNERABILITY = "Vulnerability Scan"
    COMPLIANCE = "Compliance Scan"
    NETWORK = "Network Scan"
    WEB_APPLICATION = "Web Application Scan"
    CONFIGURATION = "Configuration Scan"


# ---------- CORE MODELS ----------
class Pagination(BaseModel):
    total: Optional[int] = Field(None, description="Total number of elements", ge=0)
    limit: Optional[int] = Field(None, description="Page size", ge=1, le=100)
    offset: Optional[int] = Field(None, description="Starting position", ge=0)
    previous: Optional[int] = Field(None, description="Previous page", ge=0)
    next: Optional[int] = Field(None, description="Next page", ge=0)


class ChangeLog(BaseModel):
    createdDateTime: Optional[str] = Field(None, description="Creation timestamp", format="date-time")
    lastUpdatedDateTime: Optional[str] = Field(None, description="Last update timestamp", format="date-time")
    createdBy: Optional['User'] = Field(None, description="Created by user")
    lastUpdatedBy: Optional['User'] = Field(None, description="Last updated by user")


class User(BaseModel):
    href: Optional[str] = Field(None, description="User API endpoint URL", format="uri")
    id: Optional[str] = Field(None, description="User unique identifier", format="uuid")
    firstName: Optional[str] = Field(None, description="User first name")
    lastName: Optional[str] = Field(None, description="User last name")
    avatar: Optional['Avatar'] = Field(None, description="User avatar")


class Avatar(BaseModel):
    original: Optional[str] = Field(None, description="Original avatar URL", format="uri")
    xSmall: Optional[str] = Field(None, description="Extra small avatar URL", format="uri")
    small: Optional[str] = Field(None, description="Small avatar URL", format="uri")
    medium: Optional[str] = Field(None, description="Medium avatar URL", format="uri")
    large: Optional[str] = Field(None, description="Large avatar URL", format="uri")


class IntegrationCommonModel(BaseModel):
    href: Optional[str] = Field(None, description="Integration API endpoint URL", format="uri")
    type: Optional[str] = Field(None, description="Integration type", example="Nessus")
    id: Optional[str] = Field(None, description="Integration unique identifier", format="uuid")
    name: Optional[str] = Field(None, description="Integration name", example="Nessus Professional Scanner")


class ErrorDetails(BaseModel):
    errorCode: str = Field(..., description="Error code", pattern=r"^AP-\d{7}$")
    errorMessage: str = Field(..., description="Error message")
    statusCode: int = Field(..., description="HTTP status code")
    correlationId: Optional[str] = Field(None, description="Correlation identifier")
    details: Optional[str] = Field(None, description="Additional error details")
    property: Optional[str] = Field(None, description="Property causing error")
    help: Optional[str] = Field(None, description="Help information")
    additionalInfo: Optional[List[Dict[str, str]]] = Field(None, description="Additional error information")


# ---------- CVSS MODELS ----------
class CvssV2(BaseModel):
    accessComplexity: Optional[str] = Field(None, description="Access complexity", example="LOW")
    accessVector: Optional[str] = Field(None, description="Access vector", example="NETWORK")
    authentication: Optional[str] = Field(None, description="Authentication", example="NONE")
    availabilityImpact: Optional[str] = Field(None, description="Availability impact", example="PARTIAL")
    confidentialityImpact: Optional[str] = Field(None, description="Confidentiality impact", example="COMPLETE")
    exploitScore: Optional[float] = Field(None, description="Exploit score", example=10.0)
    impactScore: Optional[float] = Field(None, description="Impact score", example=6.9)
    integrityImpact: Optional[str] = Field(None, description="Integrity impact", example="NONE")
    score: Optional[float] = Field(None, description="CVSS v2 score", example=7.5)
    vector: Optional[str] = Field(None, description="CVSS v2 vector", example="AV:N/AC:L/Au:N/C:C/I:N/A:P")


class CvssV3(BaseModel):
    accessComplexity: Optional[str] = Field(None, description="Access complexity", example="LOW")
    attackVector: Optional[str] = Field(None, description="Attack vector", example="NETWORK")
    availabilityImpact: Optional[str] = Field(None, description="Availability impact", example="LOW")
    confidentialityImpact: Optional[str] = Field(None, description="Confidentiality impact", example="HIGH")
    exploitScore: Optional[float] = Field(None, description="Exploit score", example=3.9)
    impactScore: Optional[float] = Field(None, description="Impact score", example=4.7)
    integrityImpact: Optional[str] = Field(None, description="Integrity impact", example="NONE")
    privilegeRequired: Optional[str] = Field(None, description="Privilege required", example="NONE")
    score: Optional[float] = Field(None, description="CVSS v3 score", example=8.2)
    scope: Optional[str] = Field(None, description="Scope", example="UNCHANGED")
    userInteraction: Optional[str] = Field(None, description="User interaction", example="NONE")
    vector: Optional[str] = Field(None, description="CVSS v3 vector",
                                  example="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L")


class Link(BaseModel):
    rel: Optional[str] = Field(None, description="Relationship type")
    href: Optional[str] = Field(None, description="Link URL", format="uri")
    method: Optional[str] = Field(None, description="HTTP method")
    contentType: Optional[str] = Field(default="application/json", description="Content type")
    authenticate: Optional[bool] = Field(default=True, description="Authentication required")


class Cvss(BaseModel):
    links: Optional[List[Link]] = Field(None, description="Related links")
    v2: Optional[CvssV2] = Field(None, description="CVSS v2 information")
    v3: Optional[CvssV3] = Field(None, description="CVSS v3 information")


# ---------- VULNERABILITY MODELS ----------
class VulnerabilityResponse(BaseModel):
    # Core Information
    id: Optional[str] = Field(None, description="Vulnerability ID", example="CVE-2023-1234")
    category: Optional[List[str]] = Field(None, description="Vulnerability categories",
                                          example=["Web Application", "SQL Injection"])
    name: Optional[str] = Field(None, description="Vulnerability name",
                                example="SQL Injection vulnerability in login form")
    description: Optional[str] = Field(None, description="Vulnerability description",
                                       example="A SQL injection vulnerability exists in the user authentication system")

    # Severity and Scoring
    severity: Optional[VulnerabilitySeverity] = Field(None, description="Vulnerability severity")
    cvssScore: Optional[float] = Field(None, description="CVSS score", example=8.5)
    cvss: Optional[Cvss] = Field(None, description="CVSS details")

    # Standards and References
    cve: Optional[List[str]] = Field(None, description="CVE identifiers", example=["CVE-2023-1234", "CVE-2023-5678"])
    cwe: Optional[str] = Field(None, description="CWE identifier", example="CWE-89")

    # Status and Management
    state: Optional[VulnerabilityState] = Field(None, description="Vulnerability state")
    scan_output: Optional[str] = Field(None, description="Scanner output",
                                       example="SQL injection detected in parameter 'username'")

    # Network Information
    port: Optional[int] = Field(None, description="Port number", example=443)
    protocol: Optional[str] = Field(None, description="Protocol", example="HTTPS")
    location: Optional[str] = Field(None, description="Vulnerability location", example="/api/v1/login")

    # Timeline
    firstSeen: Optional[str] = Field(None, description="First seen timestamp", format="date-time")
    lastSeen: Optional[str] = Field(None, description="Last seen timestamp", format="date-time")

    # Audit
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class VulnerabilitiesResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[VulnerabilityResponse]] = Field(None, description="List of vulnerabilities")


# ---------- ASSET MODELS ----------
class OperatingSystem(BaseModel):
    name: Optional[str] = Field(None, description="OS name", example="Ubuntu Linux")
    version: Optional[str] = Field(None, description="OS version", example="20.04.3 LTS")


class InstalledSoftware(BaseModel):
    name: Optional[str] = Field(None, description="Software name", example="Apache HTTP Server")
    version: Optional[str] = Field(None, description="Software version", example="2.4.41")
    vendor: Optional[str] = Field(None, description="Software vendor", example="Apache Software Foundation")


class NetworkInterface(BaseModel):
    interfaceName: Optional[str] = Field(None, description="Interface name", example="eth0")
    ipAddress: Optional[str] = Field(None, description="IP address", example="192.168.1.100")
    macAddress: Optional[str] = Field(None, description="MAC address", example="00:1B:44:11:3A:B7")
    subnet: Optional[str] = Field(None, description="Subnet", example="192.168.1.0/24")


class VulnerabilitySummary(BaseModel):
    critical: Optional[str] = Field(None, description="Critical vulnerabilities count", example="2")
    high: Optional[str] = Field(None, description="High severity vulnerabilities count", example="5")
    medium: Optional[str] = Field(None, description="Medium severity vulnerabilities count", example="12")
    low: Optional[str] = Field(None, description="Low severity vulnerabilities count", example="8")


class CloudProvider(BaseModel):
    provider: Optional[str] = Field(None, description="Cloud provider", example="AWS")
    instanceId: Optional[str] = Field(None, description="Instance ID", example="i-0123456789abcdef0")
    region: Optional[str] = Field(None, description="Region", example="us-east-1")


class CloudMetaData(BaseModel):
    vpcId: Optional[str] = Field(None, description="VPC ID", example="vpc-12345678")
    subnetId: Optional[str] = Field(None, description="Subnet ID", example="subnet-87654321")
    instanceType: Optional[str] = Field(None, description="Instance type", example="t3.medium")


class Owner(BaseModel):
    name: Optional[str] = Field(None, description="Owner name", example="John Smith")
    email: Optional[str] = Field(None, description="Owner email", example="john.smith@acme-corp.com")


class Label(BaseModel):
    environment: Optional[str] = Field(None, description="Environment", example="production")
    team: Optional[str] = Field(None, description="Team", example="infrastructure")
    costCenter: Optional[str] = Field(None, description="Cost center", example="IT-OPS-001")


class AssetResponse(BaseModel):
    # Core Identity
    id: Optional[str] = Field(None, description="Asset ID", example="asset-web-server-01")
    hostname: Optional[str] = Field(None, description="Hostname", example="web-server-01")
    fqdn: Optional[str] = Field(None, description="Fully qualified domain name",
                                example="web-server-01.acme-corp.com")

    # Network Information
    ipAddresses: Optional[List[str]] = Field(None, description="IP addresses",
                                             example=["192.168.1.100", "10.0.0.15"])
    macAddresses: Optional[List[str]] = Field(None, description="MAC addresses",
                                              example=["00:1B:44:11:3A:B7", "02:1C:55:22:4B:C8"])
    networkInterfaces: Optional[List[NetworkInterface]] = Field(None, description="Network interfaces")
    openPorts: Optional[List[str]] = Field(None, description="Open ports", example=["80", "443", "22", "3389"])
    domain: Optional[str] = Field(None, description="Domain", example="acme-corp.com")
    netbiosName: Optional[str] = Field(None, description="NetBIOS name", example="WEB-SERVER-01")

    # System Information
    operatingSystem: Optional[OperatingSystem] = Field(None, description="Operating system information")
    installedSoftware: Optional[List[InstalledSoftware]] = Field(None, description="Installed software")

    # Classification and Management
    assetType: Optional[AssetType] = Field(None, description="Asset type")
    tags: Optional[List[str]] = Field(None, description="Asset tags",
                                      example=["production", "web-server", "critical"])
    labels: Optional[List[Label]] = Field(None, description="Asset labels")
    owner: Optional[Owner] = Field(None, description="Asset owner")

    # Cloud Information
    cloudProvider: Optional[CloudProvider] = Field(None, description="Cloud provider information")
    cloudMetadata: Optional[CloudMetaData] = Field(None, description="Cloud metadata")

    # Vulnerability Information
    vulnerabilitySummary: Optional[VulnerabilitySummary] = Field(None, description="Vulnerability summary")
    vulnerabilityCount: Optional[str] = Field(None, description="Total vulnerability count", example="15")
    riskScore: Optional[str] = Field(None, description="Risk score", example="7.5")
    exploitability: Optional[str] = Field(None, description="Exploitability level", example="High")

    # Scanning Information
    scanCoverage: Optional[str] = Field(None, description="Scan coverage percentage", example="95%")
    credentialedScan: Optional[bool] = Field(None, description="Whether credentialed scan was performed")
    agentId: Optional[str] = Field(None, description="Agent ID", example="agent-12345")
    lastScanTime: Optional[str] = Field(None, description="Last scan time", format="date-time")

    # Timeline
    firstSeen: Optional[str] = Field(None, description="First seen timestamp", format="date-time")
    lastSeen: Optional[str] = Field(None, description="Last seen timestamp", format="date-time")

    # Integration and Audit
    integration: Optional[IntegrationCommonModel] = Field(None, description="Integration information")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class AssetsResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[AssetResponse]] = Field(None, description="List of assets")


# ---------- SCAN MODELS ----------
class Scanner(BaseModel):
    name: Optional[str] = Field(None, description="Scanner name", example="Nessus Professional")
    type: Optional[str] = Field(None, description="Scanner type", example="Network Scanner")
    location: Optional[str] = Field(None, description="Scanner location", example="datacenter-east-1")
    scannerId: Optional[str] = Field(None, description="Scanner ID", example="scanner-nessus-001")


class ScanProfile(BaseModel):
    name: Optional[str] = Field(None, description="Scan profile name", example="Web Application Security Scan")
    id: Optional[str] = Field(None, description="Profile ID", example="profile-webapp-001")
    template: Optional[str] = Field(None, description="Scan template", example="Advanced Web Application Scan")


class VulnerabilitiesFound(BaseModel):
    critical: Optional[str] = Field(None, description="Critical vulnerabilities found", example="3")
    high: Optional[str] = Field(None, description="High severity vulnerabilities found", example="8")
    medium: Optional[str] = Field(None, description="Medium severity vulnerabilities found", example="15")
    low: Optional[str] = Field(None, description="Low severity vulnerabilities found", example="16")


class ScanResponse(BaseModel):
    # Core Information
    id: Optional[str] = Field(None, description="Scan ID", example="scan-2024-001")
    type: Optional[ScanType] = Field(None, description="Scan type")
    name: Optional[str] = Field(None, description="Scan name", example="Monthly Production Infrastructure Scan")
    description: Optional[str] = Field(None, description="Scan description",
                                       example="Comprehensive vulnerability assessment of production web servers and databases")

    # Status and Timing
    status: Optional[ScanStatus] = Field(None, description="Scan status")
    startTime: Optional[str] = Field(None, description="Scan start time", format="date-time")
    endTime: Optional[str] = Field(None, description="Scan end time", format="date-time")
    duration: Optional[str] = Field(None, description="Scan duration", example="4h 30m")

    # Scan Configuration
    scanner: Optional[Scanner] = Field(None, description="Scanner information")
    scanType: Optional[str] = Field(None, description="Scan authentication type", example="Authenticated")
    scanMode: Optional[str] = Field(None, description="Scan mode", example="Comprehensive")
    scanMethod: Optional[str] = Field(None, description="Scan method", example="Network + Agent")
    scanProfile: Optional[ScanProfile] = Field(None, description="Scan profile used")

    # Targets and Scope
    targets: Optional[List[str]] = Field(None, description="Scan targets",
                                         example=["192.168.1.0/24", "10.0.0.0/16"])
    assetIds: Optional[List[str]] = Field(None, description="Asset IDs scanned",
                                          example=["asset-web-01", "asset-db-01", "asset-api-01"])

    # Results
    findingsCount: Optional[str] = Field(None, description="Total findings count", example="42")
    vulnerabilityIds: Optional[List[str]] = Field(None, description="Vulnerability IDs found",
                                                  example=["CVE-2023-1234", "CVE-2023-5678"])
    vulnerabilitiesFound: Optional[VulnerabilitiesFound] = Field(None, description="Vulnerabilities found by severity")

    # Integration and Audit
    integration: Optional[IntegrationCommonModel] = Field(None, description="Integration information")
    changeLog: Optional[ChangeLog] = Field(None, description="Change log information")


class ScansResponse(BaseModel):
    pagination: Optional[Pagination] = Field(None, description="Pagination information")
    data: Optional[List[ScanResponse]] = Field(None, description="List of scans")


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