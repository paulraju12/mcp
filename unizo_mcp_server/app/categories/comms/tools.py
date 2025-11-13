import structlog
from typing import Dict, Any, List, Optional

from .services.comms_integration import comms_integration_service
from .services.comms_service import comms_service
from tempory.core import BaseScopedTools

logger = structlog.getLogger(__name__)


class CommsTools(BaseScopedTools):
    """MCP tools for Communications API operations"""

    def __init__(self, mcp_server):
        super().__init__(mcp_server, scope='comms')

    def _register_tools(self):
        """Register all MCP tools for communications management"""
        # Connector tools
        self.register_tool(name="comms_list_connectors")(self.list_connectors)
        self.register_tool(name="comms_list_integrations")(self.list_integrations)

        # Organization tools
        self.register_tool(name="comms_list_organizations")(self.list_organizations)
        self.register_tool(name="comms_get_organization_details")(self.get_organization_details)

        # Channel tools
        self.register_tool(name="comms_list_channels")(self.list_channels)
        self.register_tool(name="comms_get_channel_details")(self.get_channel_details)

        # Message tools
        self.register_tool(name="comms_create_message")(self.create_message)

    # ---------- CONNECTOR TOOLS ----------
    async def list_connectors(self) -> List[dict]:
        """Get list of available communication connectors"""
        logger.info("MCP tool: list_connectors called for comms")
        connectors = await comms_integration_service.get_connectors()
        return [connector.dict() if hasattr(connector, 'dict') else connector for connector in connectors]

    async def list_integrations(self, connector: str) -> List[dict]:
        """
        Get integrations for a specific communication connector.

        Args:
            connector: Name of the communication connector (e.g., 'slack', 'teams', 'discord')
        """
        logger.info(f"MCP tool: list_integrations called for comms connector: {connector}")
        integrations = await comms_integration_service.get_integrations(connector)
        return [integration.dict() if hasattr(integration, 'dict') else integration for integration in integrations]

    # ---------- ORGANIZATION TOOLS ----------
    async def list_organizations(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List organizations with pagination and sorting.

        Args:
            integration_id: Unique identifier for the communication integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name', '-createdDateTime')
        """
        logger.info(f"MCP tool: list_organizations called for integration: {integration_id}")
        return await comms_service.list_organizations(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_organization_details(
            self,
            integration_id: str,
            organization_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific organization.

        Args:
            integration_id: Unique identifier for the communication integration
            organization_id: Unique identifier of the organization to retrieve
        """
        logger.info(f"MCP tool: get_organization_details called for organization: {organization_id}")
        return await comms_service.get_organization_details(
            integration_id=integration_id,
            organization_id=organization_id
        )

    # ---------- CHANNEL TOOLS ----------
    async def list_channels(
            self,
            integration_id: str,
            organization_id: str,
            parent_id: Optional[str] = None,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List channels for an organization with filtering options.

        Args:
            integration_id: Unique identifier for the communication integration
            organization_id: Unique identifier of the organization to list channels for
            parent_id: Filter channels by their parent channel ID (returns child channels)
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name', '-createdDateTime')
        """
        logger.info(f"MCP tool: list_channels called for organization: {organization_id}")
        return await comms_service.list_channels(
            integration_id=integration_id,
            organization_id=organization_id,
            parent_id=parent_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_channel_details(
            self,
            integration_id: str,
            organization_id: str,
            channel_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific channel.

        Args:
            integration_id: Unique identifier for the communication integration
            organization_id: Unique identifier of the organization that owns the channel
            channel_id: Unique identifier of the channel to retrieve
        """
        logger.info(f"MCP tool: get_channel_details called for channel: {channel_id}")
        return await comms_service.get_channel_details(
            integration_id=integration_id,
            organization_id=organization_id,
            channel_id=channel_id
        )

    # ---------- MESSAGE TOOLS ----------
    async def create_message(
            self,
            integration_id: str,
            organization_id: str,
            channel_id: str,
            message_body: str,
            name: Optional[str] = None,
            attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a new message in a channel.

        Args:
            integration_id: Unique identifier for the communication integration
            organization_id: Unique identifier of the organization that owns the channel
            channel_id: Unique identifier of the channel to create the message in
            message_body: Content of the message to be sent (required)
            name: Subject or title of the message (optional)
            attachments: List of attachments to include with the message (optional)
        """
        logger.info(f"MCP tool: create_message called for channel: {channel_id}")
        return await comms_service.create_message(
            integration_id=integration_id,
            organization_id=organization_id,
            channel_id=channel_id,
            name=name,
            message_body=message_body,
            attachments=attachments
        )