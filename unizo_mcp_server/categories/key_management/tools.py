import structlog
from typing import Dict, Any, List, Optional

from .services.key_management_integration import key_management_integration_service
from .services.key_management_service import key_management_service
from tempory.core import BaseScopedTools

logger = structlog.getLogger(__name__)


class KeyManagementTools(BaseScopedTools):
    """MCP tools for Key Management API operations"""

    def __init__(self, mcp_server):
        super().__init__(mcp_server, scope='key_management')

    def _register_tools(self):
        """Register all MCP tools for key management"""
        # Connector tools
        self.register_tool(name="key_management_list_connectors")(self.list_connectors)
        self.register_tool(name="key_management_list_integrations")(self.list_integrations)

        # Vault configuration tools
        self.register_tool(name="key_management_list_vault_configs")(self.list_vault_configs)
        self.register_tool(name="key_management_get_vault_config_details")(self.get_vault_config_details)
        self.register_tool(name="key_management_create_vault_config")(self.create_vault_config)

    # ---------- CONNECTOR TOOLS ----------
    async def list_connectors(self) -> List[dict]:
        """Get list of available key management connectors"""
        logger.info("MCP tool: list_connectors called for key management")
        connectors = await key_management_integration_service.get_connectors()
        return [connector.dict() if hasattr(connector, 'dict') else connector for connector in connectors]

    async def list_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific key management connector"""
        logger.info(f"MCP tool: list_integrations called for key management connector: {connector}")
        integrations = await key_management_integration_service.get_integrations(connector)
        return [integration.dict() if hasattr(integration, 'dict') else integration for integration in integrations]

    # ---------- VAULT CONFIG TOOLS ----------
    async def list_vault_configs(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List vault configurations with filtering options.

        Args:
            integration_id: Unique identifier for the integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20)
            sort: Sort criteria (e.g., 'name,-createdAt')
        """
        logger.info(f"MCP tool: list_vault_configs called for integration: {integration_id}")
        return await key_management_service.list_vault_configs(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_vault_config_details(
            self,
            integration_id: str,
            vault_config_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific vault configuration.

        Args:
            integration_id: Unique identifier for the integration
            vault_config_id: Unique identifier of the vault configuration
        """
        logger.info(f"MCP tool: get_vault_config_details called for config: {vault_config_id}")
        return await key_management_service.get_vault_config_details(
            integration_id=integration_id,
            vault_config_id=vault_config_id
        )

    async def create_vault_config(
            self,
            integration_id: str,
            name: str
    ) -> Dict[str, Any]:
        """
        Create a new vault configuration.

        Args:
            integration_id: Unique identifier for the integration
            name: Name of the vault configuration
        """
        logger.info(f"MCP tool: create_vault_config called for integration: {integration_id}")
        return await key_management_service.create_vault_config(
            integration_id=integration_id,
            name=name
        )