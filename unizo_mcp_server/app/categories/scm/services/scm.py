import traceback
import structlog
from typing import Dict, Any, Optional

from .integration import scm_integration_service
from ..models.scm_models import (
    PullRequestRequest,
    PullRequestState, PullRequestVisibility
)

logger = structlog.getLogger(__name__)


class SCMService:
    async def list_organizations(self, integration_id: Optional[str] = None,
                                 offset: int = 0, limit: int = 20) -> Dict[str, Any]:
        """List all SCM organizations"""
        logger.info("Listing SCM organizations")
        try:
            organizations = await scm_integration_service.get_organizations(integration_id)

            # Apply pagination
            paginated_orgs = organizations[offset:offset + limit] if organizations else []

            result = {
                "status": "success",
                "message": f"Found {len(paginated_orgs)} organizations",
                "data": [org.dict() for org in paginated_orgs],
                "pagination": {
                    "total": len(organizations),
                    "offset": offset,
                    "limit": limit,
                    "next": offset + limit if offset + limit < len(organizations) else None,
                    "previous": offset - limit if offset > 0 else None
                }
            }

            logger.info(f"Successfully retrieved {len(paginated_orgs)} organizations")
            return result
        except Exception as e:
            logger.error(f"Error listing organizations: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_organization(self, organization_id: str, integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific SCM organization"""
        logger.info(f"Getting organization: {organization_id}")
        try:
            organization = await scm_integration_service.get_organization(organization_id, integration_id)

            if not organization:
                return {
                    "status": "error",
                    "message": f"Organization {organization_id} not found"
                }

            result = {
                "status": "success",
                "message": f"Retrieved organization: {organization_id}",
                "data": organization.dict()
            }

            logger.info(f"Successfully retrieved organization: {organization_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting organization {organization_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def list_repositories(self, organization_id: str, integration_id: Optional[str] = None,
                                offset: int = 0, limit: int = 20) -> Dict[str, Any]:
        """List repositories for an organization"""
        logger.info(f"Listing repositories for organization: {organization_id}")
        try:
            repositories = await scm_integration_service.get_repositories(
                organization_id, integration_id, offset, limit
            )

            result = {
                "status": "success",
                "message": f"Found {len(repositories)} repositories",
                "data": [repo.dict() for repo in repositories],
                "organization_id": organization_id
            }

            logger.info(f"Successfully retrieved {len(repositories)} repositories")
            return result
        except Exception as e:
            logger.error(f"Error listing repositories: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_repository(self, organization_id: str, repository_id: str,
                             integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific repository"""
        logger.info(f"Getting repository: {repository_id} in organization: {organization_id}")
        try:
            repository = await scm_integration_service.get_repository(organization_id, repository_id, integration_id)

            if not repository:
                return {
                    "status": "error",
                    "message": f"Repository {repository_id} not found in organization {organization_id}"
                }

            result = {
                "status": "success",
                "message": f"Retrieved repository: {repository_id}",
                "data": repository.dict()
            }

            logger.info(f"Successfully retrieved repository: {repository_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting repository {repository_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def list_branches(self, organization_id: str, repository_id: str,
                            integration_id: Optional[str] = None, offset: int = 0,
                            limit: int = 20, sort: Optional[str] = None) -> Dict[str, Any]:
        """List branches for a repository"""
        logger.info(f"Listing branches for repository: {repository_id}")
        try:
            branches = await scm_integration_service.get_branches(
                organization_id, repository_id, integration_id, offset, limit, sort
            )

            result = {
                "status": "success",
                "message": f"Found {len(branches)} branches",
                "data": [branch.dict() for branch in branches],
                "organization_id": organization_id,
                "repository_id": repository_id
            }

            logger.info(f"Successfully retrieved {len(branches)} branches")
            return result
        except Exception as e:
            logger.error(f"Error listing branches: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_branch(self, organization_id: str, repository_id: str, branch_id: str,
                         integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific branch"""
        logger.info(f"Getting branch: {branch_id} in repository: {repository_id}")
        try:
            branch = await scm_integration_service.get_branch(organization_id, repository_id, branch_id, integration_id)

            if not branch:
                return {
                    "status": "error",
                    "message": f"Branch {branch_id} not found in repository {repository_id}"
                }

            result = {
                "status": "success",
                "message": f"Retrieved branch: {branch_id}",
                "data": branch.dict()
            }

            logger.info(f"Successfully retrieved branch: {branch_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting branch {branch_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def list_commits(self, organization_id: str, repository_id: str,
                           integration_id: Optional[str] = None, offset: int = 0,
                           limit: int = 20, sort: Optional[str] = None) -> Dict[str, Any]:
        """List commits for a repository"""
        logger.info(f"Listing commits for repository: {repository_id}")
        try:
            commits = await scm_integration_service.get_commits(
                organization_id, repository_id, integration_id, offset, limit, sort
            )

            result = {
                "status": "success",
                "message": f"Found {len(commits)} commits",
                "data": [commit.dict() for commit in commits],
                "organization_id": organization_id,
                "repository_id": repository_id
            }

            logger.info(f"Successfully retrieved {len(commits)} commits")
            return result
        except Exception as e:
            logger.error(f"Error listing commits: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_commit(self, organization_id: str, repository_id: str, commit_id: str,
                         integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific commit"""
        logger.info(f"Getting commit: {commit_id} in repository: {repository_id}")
        try:
            commit = await scm_integration_service.get_commit(organization_id, repository_id, commit_id, integration_id)

            if not commit:
                return {
                    "status": "error",
                    "message": f"Commit {commit_id} not found in repository {repository_id}"
                }

            result = {
                "status": "success",
                "message": f"Retrieved commit: {commit_id}",
                "data": commit.dict()
            }

            logger.info(f"Successfully retrieved commit: {commit_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting commit {commit_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def list_pull_requests(self, organization_id: str, repository_id: str,
                                 integration_id: Optional[str] = None, offset: int = 0,
                                 limit: int = 20, sort: Optional[str] = None) -> Dict[str, Any]:
        """List pull requests for a repository"""
        logger.info(f"Listing pull requests for repository: {repository_id}")
        try:
            pull_requests = await scm_integration_service.get_pull_requests(
                organization_id, repository_id, integration_id, offset, limit, sort
            )

            result = {
                "status": "success",
                "message": f"Found {len(pull_requests)} pull requests",
                "data": [pr.dict() for pr in pull_requests],
                "organization_id": organization_id,
                "repository_id": repository_id
            }

            logger.info(f"Successfully retrieved {len(pull_requests)} pull requests")
            return result
        except Exception as e:
            logger.error(f"Error listing pull requests: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_pull_request(self, organization_id: str, repository_id: str, pull_request_id: str,
                               integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific pull request"""
        logger.info(f"Getting pull request: {pull_request_id} in repository: {repository_id}")
        try:
            pull_request = await scm_integration_service.get_pull_request(
                organization_id, repository_id, pull_request_id, integration_id
            )

            if not pull_request:
                return {
                    "status": "error",
                    "message": f"Pull request {pull_request_id} not found in repository {repository_id}"
                }

            result = {
                "status": "success",
                "message": f"Retrieved pull request: {pull_request_id}",
                "data": pull_request.dict()
            }

            logger.info(f"Successfully retrieved pull request: {pull_request_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting pull request {pull_request_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_pull_request(self, organization_id: str, repository_id: str,
                                  title: str, source: str, target: str,
                                  description: Optional[str] = None,
                                  state: Optional[str] = None,
                                  visibility: Optional[str] = None,
                                  integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new pull request"""
        logger.info(f"Creating pull request: {title} in repository: {repository_id}")
        try:
            pr_request = PullRequestRequest(
                title=title,
                description=description,
                source=source,
                target=target,
                state=PullRequestState(state) if state else PullRequestState.OPENED,
                visibility=PullRequestVisibility(visibility) if visibility else PullRequestVisibility.PRIVATE
            )

            pull_request = await scm_integration_service.create_pull_request(
                organization_id, repository_id, pr_request, integration_id
            )

            if not pull_request:
                return {
                    "status": "error",
                    "message": "Failed to create pull request"
                }

            result = {
                "status": "success",
                "message": f"Pull request created successfully: {pull_request.id}",
                "data": pull_request.dict()
            }

            logger.info(f"Successfully created pull request: {pull_request.id}")
            return result
        except Exception as e:
            logger.error(f"Error creating pull request: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def update_pull_request(self, organization_id: str, repository_id: str, pull_request_id: str,
                                  title: Optional[str] = None, description: Optional[str] = None,
                                  source: Optional[str] = None, target: Optional[str] = None,
                                  state: Optional[str] = None, visibility: Optional[str] = None,
                                  integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing pull request"""
        logger.info(f"Updating pull request: {pull_request_id} in repository: {repository_id}")
        try:
            # Get existing PR to maintain current values for fields not being updated
            existing_pr = await scm_integration_service.get_pull_request(
                organization_id, repository_id, pull_request_id, integration_id
            )

            if not existing_pr:
                return {
                    "status": "error",
                    "message": f"Pull request {pull_request_id} not found"
                }

            pr_request = PullRequestRequest(
                title=title or existing_pr.title or "Untitled",
                description=description if description is not None else existing_pr.description,
                source=source or "main",  # Default fallback
                target=target or "main",  # Default fallback
                state=PullRequestState(state) if state else existing_pr.state or PullRequestState.OPENED,
                visibility=PullRequestVisibility(
                    visibility) if visibility else existing_pr.visibility or PullRequestVisibility.PRIVATE
            )

            updated_pr = await scm_integration_service.update_pull_request(
                organization_id, repository_id, pull_request_id, pr_request, integration_id
            )

            if not updated_pr:
                return {
                    "status": "error",
                    "message": "Failed to update pull request"
                }

            result = {
                "status": "success",
                "message": f"Pull request updated successfully: {pull_request_id}",
                "data": updated_pr.dict()
            }

            logger.info(f"Successfully updated pull request: {pull_request_id}")
            return result
        except Exception as e:
            logger.error(f"Error updating pull request {pull_request_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


scm_service = SCMService()