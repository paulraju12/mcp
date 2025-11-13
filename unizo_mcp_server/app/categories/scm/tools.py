import structlog
from typing import Dict, Any, List, Optional

from .services.scm import scm_service,scm_integration_service
from .models.scm_models import PullRequestState, PullRequestVisibility
from tempory.core import BaseScopedTools

logger = structlog.getLogger(__name__)


class SCMTools(BaseScopedTools):
    def __init__(self, mcp_server):
        super().__init__(mcp_server,scope="scm")

    def _register_tools(self):
        """Register all MCP tools for SCM"""
        self.register_tool(name="scm_list_connectors")(self.list_connectors)
        self.register_tool(name="scm_list_integrations")(self.list_integrations)
        self.register_tool(name="scm_list_organizations")(self.list_organizations)
        self.register_tool(name="scm_get_organization")(self.get_organization)
        self.register_tool(name="scm_list_repositories")(self.list_repositories)
        self.register_tool(name="scm_get_repository")(self.get_repository)
        self.register_tool(name="scm_list_branches")(self.list_branches)
        self.register_tool(name="scm_get_branch")(self.get_branch)
        self.register_tool(name="scm_list_commits")(self.list_commits)
        self.register_tool(name="scm_get_commit")(self.get_commit)
        self.register_tool(name="scm_list_pull_requests")(self.list_pull_requests)
        self.register_tool(name="scm_get_pull_request")(self.get_pull_request)
        self.register_tool(name="scm_create_pull_request")(self.create_pull_request)
        self.register_tool(name="scm_update_pull_request")(self.update_pull_request)

    async def list_connectors(self) -> List[dict]:
        """Get list of available SCM connectors"""
        logger.info("MCP tool: list_connectors called")
        connectors = await scm_integration_service.get_connectors()
        return [connector.dict() if hasattr(connector, 'dict') else connector for connector in connectors]

    async def list_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific connector"""
        logger.info(f"MCP tool: list_integrations called for connector: {connector}")
        integrations = await scm_integration_service.get_integrations(connector)
        return [integration.dict() if hasattr(integration, 'dict') else integration for integration in integrations]


    async def list_organizations(self, integration_id: Optional[str] = None,
                                 offset: int = 0, limit: int = 20) -> Dict[str, Any]:
        """List SCM organizations"""
        logger.info("MCP tool: list_organizations called")
        return await scm_service.list_organizations(integration_id, offset, limit)

    async def get_organization(self, organization_id: str,
                               integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific SCM organization"""
        logger.info(f"MCP tool: get_organization called for: {organization_id}")
        return await scm_service.get_organization(organization_id, integration_id)

    async def list_repositories(self, organization_id: str,
                                integration_id: Optional[str] = None,
                                offset: int = 0, limit: int = 20) -> Dict[str, Any]:
        """List repositories for an organization"""
        logger.info(f"MCP tool: list_repositories called for organization: {organization_id}")
        return await scm_service.list_repositories(organization_id, integration_id, offset, limit)

    async def get_repository(self, organization_id: str, repository_id: str,
                             integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific repository"""
        logger.info(f"MCP tool: get_repository called for: {repository_id}")
        return await scm_service.get_repository(organization_id, repository_id, integration_id)

    async def list_branches(self, organization_id: str, repository_id: str,
                            integration_id: Optional[str] = None, offset: int = 0,
                            limit: int = 20, sort: Optional[str] = None) -> Dict[str, Any]:
        """List branches for a repository"""
        logger.info(f"MCP tool: list_branches called for repository: {repository_id}")
        return await scm_service.list_branches(organization_id, repository_id, integration_id, offset, limit, sort)

    async def get_branch(self, organization_id: str, repository_id: str, branch_id: str,
                         integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific branch"""
        logger.info(f"MCP tool: get_branch called for: {branch_id}")
        return await scm_service.get_branch(organization_id, repository_id, branch_id, integration_id)

    async def list_commits(self, organization_id: str, repository_id: str,
                           integration_id: Optional[str] = None, offset: int = 0,
                           limit: int = 20, sort: Optional[str] = None) -> Dict[str, Any]:
        """List commits for a repository"""
        logger.info(f"MCP tool: list_commits called for repository: {repository_id}")
        return await scm_service.list_commits(organization_id, repository_id, integration_id, offset, limit, sort)

    async def get_commit(self, organization_id: str, repository_id: str, commit_id: str,
                         integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific commit"""
        logger.info(f"MCP tool: get_commit called for: {commit_id}")
        return await scm_service.get_commit(organization_id, repository_id, commit_id, integration_id)

    async def list_pull_requests(self, organization_id: str, repository_id: str,
                                 integration_id: Optional[str] = None, offset: int = 0,
                                 limit: int = 20, sort: Optional[str] = None) -> Dict[str, Any]:
        """List pull requests for a repository"""
        logger.info(f"MCP tool: list_pull_requests called for repository: {repository_id}")
        return await scm_service.list_pull_requests(organization_id, repository_id, integration_id, offset, limit, sort)

    async def get_pull_request(self, organization_id: str, repository_id: str, pull_request_id: str,
                               integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific pull request"""
        logger.info(f"MCP tool: get_pull_request called for: {pull_request_id}")
        return await scm_service.get_pull_request(organization_id, repository_id, pull_request_id, integration_id)

    async def create_pull_request(self, organization_id: str, repository_id: str,
                                  title: str, source: str, target: str,
                                  description: Optional[str] = None,
                                  state: Optional[str] = None,
                                  visibility: Optional[str] = None,
                                  integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new pull request"""
        logger.info(f"MCP tool: create_pull_request called with title: {title}")

        # Validate enum values
        if state and state not in [s.value for s in PullRequestState]:
            return {
                "status": "error",
                "message": f"Invalid state '{state}'. Valid states are: {[s.value for s in PullRequestState]}"
            }

        if visibility and visibility not in [v.value for v in PullRequestVisibility]:
            return {
                "status": "error",
                "message": f"Invalid visibility '{visibility}'. Valid values are: {[v.value for v in PullRequestVisibility]}"
            }

        return await scm_service.create_pull_request(
            organization_id, repository_id, title, source, target,
            description, state, visibility, integration_id
        )

    async def update_pull_request(self, organization_id: str, repository_id: str, pull_request_id: str,
                                  title: Optional[str] = None, description: Optional[str] = None,
                                  source: Optional[str] = None, target: Optional[str] = None,
                                  state: Optional[str] = None, visibility: Optional[str] = None,
                                  integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing pull request"""
        logger.info(f"MCP tool: update_pull_request called for: {pull_request_id}")

        # Validate enum values
        if state and state not in [s.value for s in PullRequestState]:
            return {
                "status": "error",
                "message": f"Invalid state '{state}'. Valid states are: {[s.value for s in PullRequestState]}"
            }

        if visibility and visibility not in [v.value for v in PullRequestVisibility]:
            return {
                "status": "error",
                "message": f"Invalid visibility '{visibility}'. Valid values are: {[v.value for v in PullRequestVisibility]}"
            }

        return await scm_service.update_pull_request(
            organization_id, repository_id, pull_request_id,
            title, description, source, target, state, visibility, integration_id
        )