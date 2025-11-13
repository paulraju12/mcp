import structlog
from typing import Dict, Any, List, Optional
from .services.infra_integration import infra_integration_service
from .services.infra_service import infra_service

logger = structlog.getLogger(__name__)
from tempory.core import BaseScopedTools


class InfraTools(BaseScopedTools):
    """MCP tools for Infrastructure API operations"""

    def __init__(self, mcp_server):
        super().__init__(mcp_server, scope='infra')

    def _register_tools(self):
        """Register all MCP tools for infrastructure management"""
        # Connector discovery tools
        self.register_tool(name="infra_list_connectors")(self.list_connectors)
        self.register_tool(name="infra_list_integrations")(self.list_integrations)

        # Account tools
        self.register_tool(name="infra_list_accounts")(self.list_accounts)
        #self.register_tool(name="infra_get_account_details")(self.get_account_details)

        # Collection tools
        self.register_tool(name="infra_list_collections")(self.list_collections)
        self.register_tool(name="infra_get_collection_details")(self.get_collection_details)

        # User tools
        self.register_tool(name="infra_list_users")(self.list_users)
        self.register_tool(name="infra_get_user_details")(self.get_user_details)

        # Resource tools
        self.register_tool(name="infra_list_resources")(self.list_resources)
        self.register_tool(name="infra_get_resource_details")(self.get_resource_details)

        # Policy tools
        self.register_tool(name="infra_list_policies")(self.list_policies)
        self.register_tool(name="infra_get_policy_details")(self.get_policy_details)

        # Role tools
        self.register_tool(name="infra_list_roles")(self.list_roles)
        self.register_tool(name="infra_get_role_details")(self.get_role_details)

    # ========== CONNECTOR TOOLS ==========
    async def list_connectors(self) -> List[dict]:
        """
        Get list of available infrastructure connectors.

        Returns:
            List of connector dictionaries with 'name' field
        """
        logger.info("MCP tool: list_connectors called for infrastructure")
        connectors = await infra_integration_service.get_connectors()
        return [connector.dict() if hasattr(connector, 'dict') else connector for connector in connectors]

    async def list_integrations(self, connector: str) -> List[dict]:
        """
        Get integrations for a specific infrastructure connector.

        Args:
            connector: Name of the connector (e.g., 'aws', 'azure', 'gcp')

        Returns:
            List of integration dictionaries with 'id' and 'name' fields
        """
        logger.info(f"MCP tool: list_integrations called for infrastructure connector: {connector}")
        integrations = await infra_integration_service.get_integrations(connector)
        return [integration.dict() if hasattr(integration, 'dict') else integration for integration in integrations]

    # ========== ACCOUNT TOOLS ==========
    async def list_accounts(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List accounts with pagination.

        Args:
            integration_id: Unique identifier for the integration (UUID format)
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,-createdAt' where '-' indicates descending)

        Returns:
            Dictionary with status, message, and data containing accounts list
        """
        logger.info(f"MCP tool: list_accounts called for integration: {integration_id}")
        return await infra_service.list_accounts(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_account_details(
            self,
            integration_id: str,
            account_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific account.

        Args:
            integration_id: Unique identifier for the integration (UUID format)
            account_id: Unique identifier of the account

        Returns:
            Dictionary with status, message, and data containing account details
        """
        logger.info(f"MCP tool: get_account_details called for account: {account_id}")
        return await infra_service.get_account_details(
            integration_id=integration_id,
            account_id=account_id
        )

    # ========== COLLECTION TOOLS ==========
    async def list_collections(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List collections with pagination.

        Args:
            integration_id: Unique identifier for the integration (UUID format)
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,-createdAt' where '-' indicates descending)

        Returns:
            Dictionary with status, message, and data containing collections list
        """
        logger.info(f"MCP tool: list_collections called for integration: {integration_id}")
        return await infra_service.list_collections(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_collection_details(
            self,
            integration_id: str,
            collection_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific collection.

        Args:
            integration_id: Unique identifier for the integration (UUID format)
            collection_id: Unique identifier of the collection

        Returns:
            Dictionary with status, message, and data containing collection details
        """
        logger.info(f"MCP tool: get_collection_details called for collection: {collection_id}")
        return await infra_service.get_collection_details(
            integration_id=integration_id,
            collection_id=collection_id
        )

    # ========== USER TOOLS ==========
    async def list_users(
            self,
            integration_id: str,
            collection_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List users in a collection.

        Args:
            integration_id: Unique identifier for the integration (UUID format)
            collection_id: Unique identifier of the collection
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,emailAddress')

        Returns:
            Dictionary with status, message, and data containing users list
        """
        logger.info(f"MCP tool: list_users called for collection: {collection_id}")
        return await infra_service.list_users(
            integration_id=integration_id,
            collection_id=collection_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_user_details(
            self,
            integration_id: str,
            collection_id: str,
            user_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific user.

        Args:
            integration_id: Unique identifier for the integration (UUID format)
            collection_id: Unique identifier of the collection
            user_id: Unique identifier of the user

        Returns:
            Dictionary with status, message, and data containing user details
        """
        logger.info(f"MCP tool: get_user_details called for user: {user_id}")
        return await infra_service.get_user_details(
            integration_id=integration_id,
            collection_id=collection_id,
            user_id=user_id
        )

    # ========== RESOURCE TOOLS ==========
    async def list_resources(
            self,
            integration_id: str,
            collection_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            parent_resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List resources in a collection.

        Args:
            integration_id: Unique identifier for the integration (UUID format)
            collection_id: Unique identifier of the collection
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,-state')
            parent_resource_id: Filter by parent resource ID (optional, UUID format)

        Returns:
            Dictionary with status, message, and data containing resources list
        """
        logger.info(f"MCP tool: list_resources called for collection: {collection_id}")
        return await infra_service.list_resources(
            integration_id=integration_id,
            collection_id=collection_id,
            offset=offset,
            limit=limit,
            sort=sort,
            parent_resource_id=parent_resource_id
        )

    async def get_resource_details(
            self,
            integration_id: str,
            collection_id: str,
            resource_id: str,
            parent_resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific resource.

        Args:
            integration_id: Unique identifier for the integration (UUID format)
            collection_id: Unique identifier of the collection
            resource_id: Unique identifier of the resource
            parent_resource_id: Parent resource ID for hierarchical resources (optional, UUID format)

        Returns:
            Dictionary with status, message, and data containing resource details
        """
        logger.info(f"MCP tool: get_resource_details called for resource: {resource_id}")
        return await infra_service.get_resource_details(
            integration_id=integration_id,
            collection_id=collection_id,
            resource_id=resource_id,
            parent_resource_id=parent_resource_id
        )

    # ========== POLICY TOOLS ==========
    async def list_policies(
            self,
            integration_id: str,
            collection_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List policies in a collection.

        Args:
            integration_id: Unique identifier for the integration (UUID format)
            collection_id: Unique identifier of the collection
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,-created_at')

        Returns:
            Dictionary with status, message, and data containing policies list
        """
        logger.info(f"MCP tool: list_policies called for collection: {collection_id}")
        return await infra_service.list_policies(
            integration_id=integration_id,
            collection_id=collection_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_policy_details(
            self,
            integration_id: str,
            collection_id: str,
            policy_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific policy.

        Args:
            integration_id: Unique identifier for the integration (UUID format)
            collection_id: Unique identifier of the collection
            policy_id: Unique identifier of the policy

        Returns:
            Dictionary with status, message, and data containing policy details
        """
        logger.info(f"MCP tool: get_policy_details called for policy: {policy_id}")
        return await infra_service.get_policy_details(
            integration_id=integration_id,
            collection_id=collection_id,
            policy_id=policy_id
        )

    # ========== ROLE TOOLS ==========
    async def list_roles(
            self,
            integration_id: str,
            collection_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List roles in a collection.

        Args:
            integration_id: Unique identifier for the integration (UUID format)
            collection_id: Unique identifier of the collection
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,-created_at')

        Returns:
            Dictionary with status, message, and data containing roles list
        """
        logger.info(f"MCP tool: list_roles called for collection: {collection_id}")
        return await infra_service.list_roles(
            integration_id=integration_id,
            collection_id=collection_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_role_details(
            self,
            integration_id: str,
            collection_id: str,
            role_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific role.

        Args:
            integration_id: Unique identifier for the integration (UUID format)
            collection_id: Unique identifier of the collection
            role_id: Unique identifier of the role

        Returns:
            Dictionary with status, message, and data containing role details
        """
        logger.info(f"MCP tool: get_role_details called for role: {role_id}")
        return await infra_service.get_role_details(
            integration_id=integration_id,
            collection_id=collection_id,
            role_id=role_id
        )