import structlog
from typing import Dict, Any, List, Optional


from tempory.core import BaseScopedTools
from .services.vms_integration import vms_integration_service
from .services.vms_service import vms_service

logger = structlog.getLogger(__name__)


class VMSTools(BaseScopedTools):
    """MCP tools for VMS (Vulnerability Management System) operations"""

    def __init__(self, mcp_server):
        super().__init__(mcp_server, scope='vms')

    def _register_tools(self):
        """Register all MCP tools for VMS management"""
        logger.info("Registering VMS tools", scope=self.scope)

        # Connector discovery tools - FIXED: No parentheses allowed
        self.register_tool(name="vms_list_connectors")(self.list_connectors)
        self.register_tool(name="vms_list_integrations")(self.list_integrations)

        # Vulnerability tools
        self.register_tool(name="vms_list_vulnerabilities")(self.list_vulnerabilities)
        self.register_tool(name="vms_get_vulnerability_summary")(self.get_vulnerability_summary)

        # Asset tools
        self.register_tool(name="vms_list_assets")(self.list_assets)
        self.register_tool(name="vms_get_asset_details")(self.get_asset_details)
        self.register_tool(name="vms_get_asset_risk_assessment")(self.get_asset_risk_assessment)

        # Scan tools
        self.register_tool(name="vms_list_scans")(self.list_scans)
        self.register_tool(name="vms_get_scan_details")(self.get_scan_details)

        logger.info("VMS tools registration complete", total_tools=9)

    # ---------- CONNECTOR TOOLS ----------
    async def list_connectors(self) -> List[dict]:
        """Get list of available VMS connectors"""
        logger.info("MCP tool: list_connectors called for VMS")
        connectors = await vms_integration_service.get_connectors()
        return connectors

    async def list_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific VMS connector"""
        logger.info(f"MCP tool: list_integrations called for VMS connector: {connector}")
        integrations = await vms_integration_service.get_integrations(connector)
        return integrations

    # ---------- VULNERABILITY TOOLS ----------
    async def list_vulnerabilities(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            severity: Optional[str] = None,
            state: Optional[str] = None,
            cve: Optional[str] = None,
            search: Optional[str] = None,
            asset_id: Optional[str] = None,
            port: Optional[int] = None,
            protocol: Optional[str] = None,
            cvss_score_min: Optional[float] = None,
            cvss_score_max: Optional[float] = None,
            first_seen_from: Optional[str] = None,
            first_seen_to: Optional[str] = None,
            last_seen_from: Optional[str] = None,
            last_seen_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List vulnerabilities with comprehensive filtering options.

        Args:
            integration_id: Unique identifier for the VMS integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'severity,-cvssScore,name')
            severity: Filter by severity (Critical, High, Medium, Low, Info)
            state: Filter by state (Open, Confirmed, In Progress, Fixed, False Positive, Risk Accepted, Closed)
            cve: Filter by CVE identifier (e.g., 'CVE-2023-1234')
            search: Search vulnerabilities by name, description, or CVE
            asset_id: Filter vulnerabilities for specific asset
            port: Filter by port number
            protocol: Filter by protocol (HTTP, HTTPS, SSH, etc.)
            cvss_score_min: Minimum CVSS score filter
            cvss_score_max: Maximum CVSS score filter
            first_seen_from: Filter vulnerabilities first seen after this date (ISO format)
            first_seen_to: Filter vulnerabilities first seen before this date (ISO format)
            last_seen_from: Filter vulnerabilities last seen after this date (ISO format)
            last_seen_to: Filter vulnerabilities last seen before this date (ISO format)
        """
        logger.info(f"MCP tool: list_vulnerabilities called for integration: {integration_id}")
        return await vms_service.list_vulnerabilities(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort,
            severity=severity,
            state=state,
            cve=cve,
            search=search,
            asset_id=asset_id,
            port=port,
            protocol=protocol,
            cvss_score_min=cvss_score_min,
            cvss_score_max=cvss_score_max,
            first_seen_from=first_seen_from,
            first_seen_to=first_seen_to,
            last_seen_from=last_seen_from,
            last_seen_to=last_seen_to
        )

    async def get_vulnerability_summary(
            self,
            integration_id: str,
            group_by: Optional[str] = None,
            filter_severity: Optional[List[str]] = None,
            filter_state: Optional[List[str]] = None,
            date_range_from: Optional[str] = None,
            date_range_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get vulnerability summary and statistics.

        Args:
            integration_id: Unique identifier for the VMS integration
            group_by: Group results by field (severity, state, asset_type, etc.)
            filter_severity: List of severity levels to include
            filter_state: List of states to include
            date_range_from: Start date for filtering (ISO format)
            date_range_to: End date for filtering (ISO format)
        """
        logger.info(f"MCP tool: get_vulnerability_summary called for integration: {integration_id}")
        return await vms_service.get_vulnerability_summary(
            integration_id=integration_id,
            group_by=group_by,
            filter_severity=filter_severity,
            filter_state=filter_state,
            date_range_from=date_range_from,
            date_range_to=date_range_to
        )

    # ---------- ASSET TOOLS ----------
    async def list_assets(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            asset_type: Optional[str] = None,
            operating_system: Optional[str] = None,
            ip_address: Optional[str] = None,
            hostname: Optional[str] = None,
            domain: Optional[str] = None,
            tags: Optional[List[str]] = None,
            has_vulnerabilities: Optional[bool] = None,
            risk_score_min: Optional[float] = None,
            risk_score_max: Optional[float] = None,
            last_scan_from: Optional[str] = None,
            last_scan_to: Optional[str] = None,
            cloud_provider: Optional[str] = None,
            environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List assets with comprehensive filtering options.

        Args:
            integration_id: Unique identifier for the VMS integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'hostname,-riskScore,lastScanTime')
            asset_type: Filter by asset type (Server, Workstation, Mobile, etc.)
            operating_system: Filter by OS (Windows, Linux, macOS, etc.)
            ip_address: Filter by IP address or subnet (e.g., '192.168.1.0/24')
            hostname: Filter by hostname pattern
            domain: Filter by domain name
            tags: Filter by asset tags
            has_vulnerabilities: Filter assets with/without vulnerabilities
            risk_score_min: Minimum risk score filter
            risk_score_max: Maximum risk score filter
            last_scan_from: Filter assets scanned after this date (ISO format)
            last_scan_to: Filter assets scanned before this date (ISO format)
            cloud_provider: Filter by cloud provider (AWS, Azure, GCP, etc.)
            environment: Filter by environment tag (production, staging, development)
        """
        logger.info(f"MCP tool: list_assets called for integration: {integration_id}")
        return await vms_service.list_assets(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort,
            asset_type=asset_type,
            operating_system=operating_system,
            ip_address=ip_address,
            hostname=hostname,
            domain=domain,
            tags=tags,
            has_vulnerabilities=has_vulnerabilities,
            risk_score_min=risk_score_min,
            risk_score_max=risk_score_max,
            last_scan_from=last_scan_from,
            last_scan_to=last_scan_to,
            cloud_provider=cloud_provider,
            environment=environment
        )

    async def get_asset_details(
            self,
            integration_id: str,
            asset_id: str,
            include_vulnerabilities: Optional[bool] = None,
            include_scan_history: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific asset.

        Args:
            integration_id: Unique identifier for the VMS integration
            asset_id: Unique identifier of the asset
            include_vulnerabilities: Include vulnerability details in response
            include_scan_history: Include scan history in response
        """
        logger.info(f"MCP tool: get_asset_details called for asset: {asset_id}")
        return await vms_service.get_asset_details(
            integration_id=integration_id,
            asset_id=asset_id,
            include_vulnerabilities=include_vulnerabilities,
            include_scan_history=include_scan_history
        )

    async def get_asset_risk_assessment(
            self,
            integration_id: str,
            asset_id: Optional[str] = None,
            top_n: int = 10,
            risk_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get asset risk assessment and rankings.

        Args:
            integration_id: Unique identifier for the VMS integration
            asset_id: Specific asset ID for individual assessment (optional)
            top_n: Number of top risky assets to return (default: 10)
            risk_threshold: Minimum risk score threshold for inclusion
        """
        logger.info(f"MCP tool: get_asset_risk_assessment called for integration: {integration_id}")
        return await vms_service.get_asset_risk_assessment(
            integration_id=integration_id,
            asset_id=asset_id,
            top_n=top_n,
            risk_threshold=risk_threshold
        )

    # ---------- SCAN TOOLS ----------
    async def list_scans(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            scan_type: Optional[str] = None,
            status: Optional[str] = None,
            scanner_name: Optional[str] = None,
            target: Optional[str] = None,
            start_time_from: Optional[str] = None,
            start_time_to: Optional[str] = None,
            end_time_from: Optional[str] = None,
            end_time_to: Optional[str] = None,
            has_findings: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        List scans with filtering options.

        Args:
            integration_id: Unique identifier for the VMS integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'startTime,-duration,name')
            scan_type: Filter by scan type (Vulnerability Scan, Compliance Scan, etc.)
            status: Filter by scan status (Pending, Running, Completed, Failed, Cancelled)
            scanner_name: Filter by scanner name or type
            target: Filter by scan target (IP range, hostname, etc.)
            start_time_from: Filter scans started after this date (ISO format)
            start_time_to: Filter scans started before this date (ISO format)
            end_time_from: Filter scans completed after this date (ISO format)
            end_time_to: Filter scans completed before this date (ISO format)
            has_findings: Filter scans with/without findings
        """
        logger.info(f"MCP tool: list_scans called for integration: {integration_id}")
        return await vms_service.list_scans(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort,
            scan_type=scan_type,
            status=status,
            scanner_name=scanner_name,
            target=target,
            start_time_from=start_time_from,
            start_time_to=start_time_to,
            end_time_from=end_time_from,
            end_time_to=end_time_to,
            has_findings=has_findings
        )

    async def get_scan_details(
            self,
            integration_id: str,
            scan_id: str,
            include_assets: Optional[bool] = None,
            include_vulnerabilities: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific scan.

        Args:
            integration_id: Unique identifier for the VMS integration
            scan_id: Unique identifier of the scan
            include_assets: Include scanned assets in response
            include_vulnerabilities: Include discovered vulnerabilities in response
        """
        logger.info(f"MCP tool: get_scan_details called for scan: {scan_id}")
        return await vms_service.get_scan_details(
            integration_id=integration_id,
            scan_id=scan_id,
            include_assets=include_assets,
            include_vulnerabilities=include_vulnerabilities
        )