import structlog
from typing import Dict, Any, List, Optional

from .services.observability_integration import observability_integration_service
from .services.observability_service import observability_service
from tempory.core import BaseScopedTools

logger = structlog.getLogger(__name__)


class ObservabilityTools(BaseScopedTools):
    """MCP tools for Observability API operations"""

    def __init__(self, mcp_server):
        super().__init__(mcp_server, scope='observability')

    def _register_tools(self):
        """Register all MCP tools for observability management"""
        # Connector tools
        self.register_tool(name="observability_list_connectors")(self.list_connectors)
        self.register_tool(name="observability_list_integrations")(self.list_integrations)

        # Log tools
        self.register_tool(name="observability_list_logs")(self.list_logs)
        self.register_tool(name="observability_get_log_details")(self.get_log_details)


    # ---------- CONNECTOR TOOLS ----------
    async def list_connectors(self) -> List[dict]:
        """Get list of available observability connectors"""
        logger.info("MCP tool: list_connectors called for observability")
        connectors = await observability_integration_service.get_connectors()
        return [connector.dict() if hasattr(connector, 'dict') else connector for connector in connectors]

    async def list_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific observability connector"""
        logger.info(f"MCP tool: list_integrations called for observability connector: {connector}")
        integrations = await observability_integration_service.get_integrations(connector)
        return [integration.dict() if hasattr(integration, 'dict') else integration for integration in integrations]

    # ---------- LOG TOOLS ----------
    async def list_logs(
            self,
            integration_id: str,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List logs with pagination and sorting options.

        Args:
            integration_id: Unique identifier for the integration
            offset: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 20)
            sort: Field to sort by, prefixed with '-' for descending order (e.g., '-timestamp', 'level')
        """
        logger.info(f"MCP tool: list_logs called for integration: {integration_id}")
        return await observability_service.list_logs(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_log_details(
            self,
            integration_id: str,
            log_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific log entry.

        Args:
            integration_id: Unique identifier for the integration
            log_id: Unique identifier of the log entry
        """
        logger.info(f"MCP tool: get_log_details called for log: {log_id}")
        return await observability_service.get_log_details(
            integration_id=integration_id,
            log_id=log_id
        )