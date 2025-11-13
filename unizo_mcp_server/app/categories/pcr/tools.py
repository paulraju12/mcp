import structlog
from typing import Dict, Any, List, Optional

from .services.pcr_integration import pcr_integration_service
from .services.pcr_service import pcr_service
from tempory.core import BaseScopedTools

logger = structlog.getLogger(__name__)


class PCRTools(BaseScopedTools):
    """MCP tools for PCR API operations"""

    def __init__(self, mcp_server):
        super().__init__(mcp_server,scope="pcr")

    def _register_tools(self):
        """Register all MCP tools for PCR management"""
        # Connector tools
        self.register_tool(name="pcr_list_connectors")(self.list_connectors)
        self.register_tool(name="pcr_list_integrations")(self.list_integrations)

        # Organization tools
        self.register_tool(name="pcr_list_organizations")(self.list_organizations)
        self.register_tool(name="pcr_get_organization_details")(self.get_organization_details)

        # Repository tools
        self.register_tool(name="pcr_list_repositories")(self.list_repositories)
        self.register_tool(name="pcr_get_repository_details")(self.get_repository_details)

        # Artifact tools
        self.register_tool(name="pcr_list_artifacts")(self.list_artifacts)
        self.register_tool(name="pcr_get_artifact_details")(self.get_artifact_details)

        # Tag tools
        self.register_tool(name="pcr_list_tags")(self.list_tags)
        self.register_tool(name="pcr_get_tag_details")(self.get_tag_details)

    # ---------- CONNECTOR TOOLS ----------
    async def list_connectors(self) -> List[dict]:
        """Get list of available PCR connectors"""
        logger.info("MCP tool: list_connectors called for PCR")
        connectors = await pcr_integration_service.get_connectors()
        return [connector.dict() if hasattr(connector, 'dict') else connector for connector in connectors]

    async def list_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific PCR connector"""
        logger.info(f"MCP tool: list_integrations called for PCR connector: {connector}")
        integrations = await pcr_integration_service.get_integrations(connector)
        return [integration.dict() if hasattr(integration, 'dict') else integration for integration in integrations]

    # ---------- ORGANIZATION TOOLS ----------
    async def list_organizations(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20
    ) -> Dict[str, Any]:
        """
        List organizations in the packaging and container registry.

        Args:
            integration_id: Unique identifier for the integration
            offset: Number of items to skip for pagination (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
        """
        logger.info(f"MCP tool: list_organizations called for integration: {integration_id}")
        return await pcr_service.list_organizations(
            integration_id=integration_id,
            offset=offset,
            limit=limit
        )

    async def get_organization_details(
            self,
            integration_id: str,
            organization_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific organization.

        Args:
            integration_id: Unique identifier for the integration
            organization_id: Unique identifier of the organization
        """
        logger.info(f"MCP tool: get_organization_details called for organization: {organization_id}")
        return await pcr_service.get_organization_details(
            integration_id=integration_id,
            organization_id=organization_id
        )

    # ---------- REPOSITORY TOOLS ----------
    async def list_repositories(
            self,
            integration_id: str,
            organization_id: str,
            offset: int = 0,
            limit: int = 20
    ) -> Dict[str, Any]:
        """
        List repositories for a specific organization.

        Args:
            integration_id: Unique identifier for the integration
            organization_id: Unique identifier of the organization
            offset: Number of items to skip for pagination (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
        """
        logger.info(f"MCP tool: list_repositories called for organization: {organization_id}")
        return await pcr_service.list_repositories(
            integration_id=integration_id,
            organization_id=organization_id,
            offset=offset,
            limit=limit
        )

    async def get_repository_details(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific repository.

        Args:
            integration_id: Unique identifier for the integration
            organization_id: Unique identifier of the organization
            repository_id: Unique identifier of the repository
        """
        logger.info(f"MCP tool: get_repository_details called for repository: {repository_id}")
        return await pcr_service.get_repository_details(
            integration_id=integration_id,
            organization_id=organization_id,
            repository_id=repository_id
        )

    # ---------- ARTIFACT TOOLS ----------
    async def list_artifacts(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List artifacts for a specific repository.

        Args:
            integration_id: Unique identifier for the integration
            organization_id: Unique identifier of the organization
            repository_id: Unique identifier of the repository
            offset: Number of items to skip for pagination (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Field to sort by and sort direction (e.g., 'name', '-createdDateTime')
        """
        logger.info(f"MCP tool: list_artifacts called for repository: {repository_id}")
        return await pcr_service.list_artifacts(
            integration_id=integration_id,
            organization_id=organization_id,
            repository_id=repository_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_artifact_details(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str,
            artifact_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific artifact.

        Args:
            integration_id: Unique identifier for the integration
            organization_id: Unique identifier of the organization
            repository_id: Unique identifier of the repository
            artifact_id: Unique identifier of the artifact
        """
        logger.info(f"MCP tool: get_artifact_details called for artifact: {artifact_id}")
        return await pcr_service.get_artifact_details(
            integration_id=integration_id,
            organization_id=organization_id,
            repository_id=repository_id,
            artifact_id=artifact_id
        )

    # ---------- TAG TOOLS ----------
    async def list_tags(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str,
            artifact_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List tags for a specific artifact.

        Args:
            integration_id: Unique identifier for the integration
            organization_id: Unique identifier of the organization
            repository_id: Unique identifier of the repository
            artifact_id: Unique identifier of the artifact
            offset: Number of items to skip for pagination (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Field to sort by and sort direction (e.g., 'name', '-createdDateTime')
        """
        logger.info(f"MCP tool: list_tags called for artifact: {artifact_id}")
        return await pcr_service.list_tags(
            integration_id=integration_id,
            organization_id=organization_id,
            repository_id=repository_id,
            artifact_id=artifact_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_tag_details(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str,
            artifact_id: str,
            tag_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific tag.

        Args:
            integration_id: Unique identifier for the integration
            organization_id: Unique identifier of the organization
            repository_id: Unique identifier of the repository
            artifact_id: Unique identifier of the artifact
            tag_id: Unique identifier of the tag
        """
        logger.info(f"MCP tool: get_tag_details called for tag: {tag_id}")
        return await pcr_service.get_tag_details(
            integration_id=integration_id,
            organization_id=organization_id,
            repository_id=repository_id,
            artifact_id=artifact_id,
            tag_id=tag_id
        )