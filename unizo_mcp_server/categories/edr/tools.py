import structlog
from typing import Dict, Any, List, Optional

from .services.edr_integration import edr_integration_service
from .services.edr_service import edr_service
from tempory.core import BaseScopedTools

logger = structlog.getLogger(__name__)


class EDRTools(BaseScopedTools):
    """MCP tools for EDR API operations"""

    def __init__(self, mcp_server):
        super().__init__(mcp_server, scope='edr')

    def _register_tools(self):
        """Register all MCP tools for EDR management"""
        # Connector tools
        self.register_tool(name="edr_list_connectors")(self.list_connectors)
        self.register_tool(name="edr_list_integrations")(self.list_integrations)

        # Device tools
        self.register_tool(name="edr_list_devices")(self.list_devices)
        self.register_tool(name="edr_get_device_details")(self.get_device_details)

        # Device alert tools
        self.register_tool(name="edr_list_device_alerts")(self.list_device_alerts)
        self.register_tool(name="edr_get_device_alert_details")(self.get_device_alert_details)

    # ---------- CONNECTOR TOOLS ----------
    async def list_connectors(self) -> List[dict]:
        """
        Get list of available EDR connectors.

        Returns:
            List of available EDR connectors with their names.
        """
        logger.info("MCP tool: list_connectors called for edr")
        try:
            connectors = await edr_integration_service.get_connectors()
            return [connector.dict() if hasattr(connector, 'dict') else connector for connector in connectors]
        except Exception as e:
            logger.error(f"Error in list_connectors: {str(e)}")
            return []

    async def list_integrations(self, connector: str) -> List[dict]:
        """
        Get integrations for a specific EDR connector.

        Args:
            connector: Name of the EDR connector (e.g., "crowdstrike", "sentinelone")

        Returns:
            List of available integrations for the specified connector.
        """
        logger.info(f"MCP tool: list_integrations called for edr connector: {connector}")
        try:
            integrations = await edr_integration_service.get_integrations(connector)
            return [integration.dict() if hasattr(integration, 'dict') else integration for integration in integrations]
        except Exception as e:
            logger.error(f"Error in list_integrations: {str(e)}")
            return []

    # ---------- DEVICE TOOLS ----------
    async def list_devices(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List devices with pagination and sorting.

        Args:
            integration_id: Unique identifier for the integration (required)
            offset: Number of items to skip (default: 0, minimum: 0)
            limit: Maximum number of items to return (default: 20, range: 1-100)
            sort: Sort criteria using comma-separated field names.
                  Prefix with '-' for descending order.
                  Examples: "id", "-state", "platform.name,-id"

        Returns:
            Dictionary containing:
            - status: "success" or "error"
            - message: Description of the operation result
            - data: Object with devices list, pagination info, and total count

        Example:
            {
                "status": "success",
                "message": "Retrieved 15 devices",
                "data": {
                    "devices": [...],
                    "pagination": {...},
                    "total_count": 150
                }
            }
        """
        logger.info(f"MCP tool: list_devices called for integration: {integration_id}")
        return await edr_service.list_devices(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_device_details(
            self,
            integration_id: str,
            device_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific device.

        Args:
            integration_id: Unique identifier for the integration (required)
            device_id: Unique identifier of the device (required)
                       Examples: "DESKTOP-ABC123", "SERVER-DEF456"

        Returns:
            Dictionary containing:
            - status: "success" or "error"
            - message: Description of the operation result
            - data: Object with complete device information

        Device information includes:
            - Basic info: ID, state, hostnames, FQDNs
            - Network: IPv4/IPv6 addresses, MAC addresses
            - Platform: OS details, platform type
            - Security: Installed agents, policies, software inventory
            - Infrastructure: Active Directory info, cloud metadata
            - Metadata: Tags, identities, change log

        Example:
            {
                "status": "success",
                "message": "Retrieved device details for DESKTOP-ABC123",
                "data": {
                    "device": {
                        "id": "DESKTOP-ABC123",
                        "state": "ACTIVE",
                        "platform": {...},
                        "os": {...},
                        "hostnames": [...],
                        "ipv4s": [...],
                        ...
                    }
                }
            }
        """
        logger.info(f"MCP tool: get_device_details called for device: {device_id}")
        return await edr_service.get_device_details(
            integration_id=integration_id,
            device_id=device_id
        )

    # ---------- DEVICE ALERT TOOLS ----------
    async def list_device_alerts(
            self,
            integration_id: str,
            device_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List alerts for a specific device.

        Args:
            integration_id: Unique identifier for the integration (required)
            device_id: Unique identifier of the device (required)
            offset: Number of items to skip (default: 0, minimum: 0)
            limit: Maximum number of items to return (default: 20, range: 1-100)
            sort: Sort criteria using comma-separated field names.
                  Prefix with '-' for descending order.
                  Examples: "severity", "-createdDateTime", "title,severity"

        Returns:
            Dictionary containing:
            - status: "success" or "error"
            - message: Description of the operation result
            - data: Object with alerts list, pagination info, device ID, and total count

        Alert information includes:
            - Basic info: ID, state, title, description, severity
            - Source: Vendor information, source system
            - Status: Internal and external status tracking
            - Audit: Change log with creation/update timestamps

        Example:
            {
                "status": "success",
                "message": "Retrieved 5 alerts for device DESKTOP-ABC123",
                "data": {
                    "alerts": [...],
                    "pagination": {...},
                    "device_id": "DESKTOP-ABC123",
                    "total_count": 25
                }
            }
        """
        logger.info(f"MCP tool: list_device_alerts called for device: {device_id}")
        return await edr_service.list_device_alerts(
            integration_id=integration_id,
            device_id=device_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_device_alert_details(
            self,
            integration_id: str,
            device_id: str,
            alert_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific device alert.

        Args:
            integration_id: Unique identifier for the integration (required)
            device_id: Unique identifier of the device (required)
            alert_id: Unique identifier of the alert (required, UUID format)
                     Example: "550e8400-e29b-41d4-a716-446655440000"

        Returns:
            Dictionary containing:
            - status: "success" or "error"
            - message: Description of the operation result
            - data: Object with complete alert information and device ID

        Alert details include:
            - Core info: ID, state, title, description, severity
            - Vendor details: Vendor ID, vendor-specific severity and status
            - Source information: Originating security system
            - Status tracking: Internal and external status management
            - Audit trail: Creation and modification timestamps with user info

        Example:
            {
                "status": "success",
                "message": "Retrieved alert details for ALT-2024-001-MALWARE",
                "data": {
                    "alert": {
                        "id": "ALT-2024-001-MALWARE",
                        "state": "ACTIVE",
                        "title": "Suspicious Process Execution Detected",
                        "description": "A potentially malicious process...",
                        "severity": "HIGH",
                        "vendor": {...},
                        "source": {...},
                        "status": {...},
                        "changeLog": {...}
                    },
                    "device_id": "DESKTOP-ABC123"
                }
            }
        """
        logger.info(f"MCP tool: get_device_alert_details called for alert: {alert_id}")
        return await edr_service.get_device_alert_details(
            integration_id=integration_id,
            device_id=device_id,
            alert_id=alert_id
        )