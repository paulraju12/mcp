import structlog
from typing import List, Dict, Any, Optional
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request
from ..models.scm_models import (
    Organization, Repository, Branch, Commit, PullRequest, PullRequestRequest
)

logger = structlog.getLogger(__name__)


class SCMIntegrationService:

    async def get_connectors(self) -> List[dict]:
        """Get list of available SCM connectors"""
        logger.info("Getting list of SCM connectors")
        try:
            headers = extract_headers_from_request()

            # Build filter - ONLY organization/suborganization filter
            filter_conditions = []

            # Check for suborganizationId first
            suborganization_id = headers.get("suborganizationId")
            organization_id = headers.get("organizationId")

            if suborganization_id:
                # If suborganizationId exists, filter by subOrganization/externalKey
                filter_conditions.append({
                    "property": "/subOrganization/externalKey",
                    "operator": "=",
                    "values": [suborganization_id]
                })
                logger.info(f"Filtering by subOrganization/externalKey: {suborganization_id}")
            elif organization_id:
                # If no suborganizationId, filter by organization/id
                filter_conditions.append({
                    "property": "/organization/id",
                    "operator": "=",
                    "values": [organization_id]
                })
                logger.info(f"Filtering by organization/id: {organization_id}")
            else:
                logger.warning("No suborganizationId or organizationId found - returning all results")

            payload = {
                "filter": {
                    "and": filter_conditions
                },
                "pagination": {"offset": 0, "limit": 999}
            }

            url = f"{settings.integration_mgr_base_url}/api/v1/integrations/search"
            response: Dict[str, Any] = await http_client_service.make_request("post", url, headers, json_data=payload)
            integrations = response.get("data", [])

            logger.info(f"Retrieved {len(integrations)} total integrations from API")

            # Filter for SCM type in code
            connectors = []
            seen_connectors = set()
            for integ in integrations:
                # Check if it's a SCM integration
                if integ.get("type") == "SCM" and "serviceProfile" in integ and "name" in integ["serviceProfile"]:
                    connector_name = integ["serviceProfile"]["name"].lower()
                    if connector_name not in seen_connectors:
                        connectors.append({"name": connector_name})
                        seen_connectors.add(connector_name)

            logger.info(f"Found {len(connectors)} SCM connectors after filtering")
            return connectors
        except Exception as e:
            logger.error(f"Error getting SCM connectors: {str(e)}")
            return []

    async def get_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific SCM connector"""
        logger.info(f"Getting SCM integrations for connector: {connector}")
        try:
            headers = extract_headers_from_request()

            # Build filter - ONLY organization/suborganization filter
            filter_conditions = []

            # Check for suborganizationId first
            suborganization_id = headers.get("suborganizationId")
            organization_id = headers.get("organizationId")

            if suborganization_id:
                # If suborganizationId exists, filter by subOrganization/externalKey
                filter_conditions.append({
                    "property": "/subOrganization/externalKey",
                    "operator": "=",
                    "values": [suborganization_id]
                })
                logger.info(f"Filtering by subOrganization/externalKey: {suborganization_id}")
            elif organization_id:
                # If no suborganizationId, filter by organization/id
                filter_conditions.append({
                    "property": "/organization/id",
                    "operator": "=",
                    "values": [organization_id]
                })
                logger.info(f"Filtering by organization/id: {organization_id}")
            else:
                logger.warning("No suborganizationId or organizationId found - returning all results")

            payload = {
                "filter": {
                    "and": filter_conditions
                },
                "pagination": {"offset": 0, "limit": 999}
            }

            url = f"{settings.integration_mgr_base_url}/api/v1/integrations/search"
            response = await http_client_service.make_request("post", url, headers, json_data=payload)
            integrations = response.get("data", [])

            logger.info(f"Retrieved {len(integrations)} total integrations from API")

            # Filter for SCM type and matching connector name in code
            matching_integrations = [
                {"id": integ.get("id"), "name": integ.get("name", "Unnamed Integration")}
                for integ in integrations
                if integ.get("type") == "SCM" and
                   "serviceProfile" in integ and
                   "name" in integ["serviceProfile"] and
                   integ["serviceProfile"]["name"].lower() == connector.lower()
            ]

            logger.info(f"Found {len(matching_integrations)} integrations for SCM connector {connector} after filtering")
            return matching_integrations
        except Exception as e:
            logger.error(f"Error getting SCM integrations: {str(e)}")
            return []

    async def get_organizations(self, integration_id: Optional[str] = None) -> List[Organization]:
        """Get list of SCM organizations"""
        logger.info("Getting list of SCM organizations")
        try:
            headers = extract_headers_from_request()
            if integration_id:
                headers["integrationId"] = integration_id

            url = f"{settings.scm_api_base_url}/api/v1/scm/organizations"
            response = await http_client_service.make_request("get", url, headers)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                response_data = response.json()
            else:
                response_data = response

            organizations_data = response_data.get("data", [])

            organizations = []
            for org_data in organizations_data:
                organizations.append(Organization(**org_data))

            logger.info(f"Found {len(organizations)} organizations")
            return organizations
        except Exception as e:
            logger.error(f"Error getting organizations: {str(e)}")
            return []

    async def get_organization(self, organization_id: str, integration_id: Optional[str] = None) -> Optional[
        Organization]:
        """Get a specific SCM organization"""
        logger.info(f"Getting organization: {organization_id}")
        try:
            headers = extract_headers_from_request()
            if integration_id:
                headers["integrationId"] = integration_id

            url = f"{settings.scm_api_base_url}/api/v1/scm/organizations/{organization_id}"
            response = await http_client_service.make_request("get", url, headers)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                org_data = response.json()
            else:
                org_data = response

            organization = Organization(**org_data)
            logger.info(f"Retrieved organization: {organization_id}")
            return organization
        except Exception as e:
            logger.error(f"Error getting organization {organization_id}: {str(e)}")
            return None

    async def get_repositories(self, organization_id: str, integration_id: Optional[str] = None,
                               offset: int = 0, limit: int = 20) -> List[Repository]:
        """Get list of repositories for an organization"""
        logger.info(f"Getting repositories for organization: {organization_id}")
        try:
            headers = extract_headers_from_request()
            if integration_id:
                headers["integrationId"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }

            url = f"{settings.scm_api_base_url}/api/v1/scm/organizations/{organization_id}/repositories"
            response = await http_client_service.make_request("get", url, headers, params=params)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                response_data = response.json()
            else:
                response_data = response

            repos_data = response_data.get("data", [])

            repositories = []
            for repo_data in repos_data:
                repositories.append(Repository(**repo_data))

            logger.info(f"Found {len(repositories)} repositories")
            return repositories
        except Exception as e:
            logger.error(f"Error getting repositories: {str(e)}")
            return []

    async def get_repository(self, organization_id: str, repository_id: str,
                             integration_id: Optional[str] = None) -> Optional[Repository]:
        """Get a specific repository"""
        logger.info(f"Getting repository: {repository_id} in organization: {organization_id}")
        try:
            headers = extract_headers_from_request()
            if integration_id:
                headers["integrationId"] = integration_id

            url = f"{settings.scm_api_base_url}/api/v1/scm/organizations/{organization_id}/repositories/{repository_id}"
            response = await http_client_service.make_request("get", url, headers)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                repo_data = response.json()
            else:
                repo_data = response

            repository = Repository(**repo_data)
            logger.info(f"Retrieved repository: {repository_id}")
            return repository
        except Exception as e:
            logger.error(f"Error getting repository {repository_id}: {str(e)}")
            return None

    async def get_branches(self, organization_id: str, repository_id: str,
                           integration_id: Optional[str] = None, offset: int = 0,
                           limit: int = 20, sort: Optional[str] = None) -> List[Branch]:
        """Get branches for a repository"""
        logger.info(f"Getting branches for repository: {repository_id}")
        try:
            headers = extract_headers_from_request()
            if integration_id:
                headers["integrationId"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }
            if sort:
                params["sort"] = sort

            url = f"{settings.scm_api_base_url}/api/v1/scm/organizations/{organization_id}/repositories/{repository_id}/branches"
            response = await http_client_service.make_request("get", url, headers, params=params)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                response_data = response.json()
            else:
                response_data = response

            branches_data = response_data.get("data", [])

            branches = []
            for branch_data in branches_data:
                branches.append(Branch(**branch_data))

            logger.info(f"Found {len(branches)} branches")
            return branches
        except Exception as e:
            logger.error(f"Error getting branches: {str(e)}")
            return []

    async def get_branch(self, organization_id: str, repository_id: str, branch_id: str,
                         integration_id: Optional[str] = None) -> Optional[Branch]:
        """Get a specific branch"""
        logger.info(f"Getting branch: {branch_id} in repository: {repository_id}")
        try:
            headers = extract_headers_from_request()
            if integration_id:
                headers["integrationId"] = integration_id

            url = f"{settings.scm_api_base_url}/api/v1/scm/organizations/{organization_id}/repositories/{repository_id}/branches/{branch_id}"
            response = await http_client_service.make_request("get", url, headers)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                branch_data = response.json()
            else:
                branch_data = response

            branch = Branch(**branch_data)
            logger.info(f"Retrieved branch: {branch_id}")
            return branch
        except Exception as e:
            logger.error(f"Error getting branch {branch_id}: {str(e)}")
            return None

    async def get_commits(self, organization_id: str, repository_id: str,
                          integration_id: Optional[str] = None, offset: int = 0,
                          limit: int = 20, sort: Optional[str] = None) -> List[Commit]:
        """Get commits for a repository"""
        logger.info(f"Getting commits for repository: {repository_id}")
        try:
            headers = extract_headers_from_request()
            if integration_id:
                headers["integrationId"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }
            if sort:
                params["sort"] = sort

            url = f"{settings.scm_api_base_url}/api/v1/scm/organizations/{organization_id}/repositories/{repository_id}/commits"
            response = await http_client_service.make_request("get", url, headers, params=params)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                response_data = response.json()
            else:
                response_data = response

            commits_data = response_data.get("data", [])

            commits = []
            for commit_data in commits_data:
                commits.append(Commit(**commit_data))

            logger.info(f"Found {len(commits)} commits")
            return commits
        except Exception as e:
            logger.error(f"Error getting commits: {str(e)}")
            return []

    async def get_commit(self, organization_id: str, repository_id: str, commit_id: str,
                         integration_id: Optional[str] = None) -> Optional[Commit]:
        """Get a specific commit"""
        logger.info(f"Getting commit: {commit_id} in repository: {repository_id}")
        try:
            headers = extract_headers_from_request()
            if integration_id:
                headers["integrationId"] = integration_id

            url = f"{settings.scm_api_base_url}/api/v1/scm/organizations/{organization_id}/repositories/{repository_id}/commits/{commit_id}"
            response = await http_client_service.make_request("get", url, headers)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                commit_data = response.json()
            else:
                commit_data = response

            commit = Commit(**commit_data)
            logger.info(f"Retrieved commit: {commit_id}")
            return commit
        except Exception as e:
            logger.error(f"Error getting commit {commit_id}: {str(e)}")
            return None

    async def get_pull_requests(self, organization_id: str, repository_id: str,
                                integration_id: Optional[str] = None, offset: int = 0,
                                limit: int = 20, sort: Optional[str] = None) -> List[PullRequest]:
        """Get pull requests for a repository"""
        logger.info(f"Getting pull requests for repository: {repository_id}")
        try:
            headers = extract_headers_from_request()
            if integration_id:
                headers["integrationId"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }
            if sort:
                params["sort"] = sort

            url = f"{settings.scm_api_base_url}/api/v1/scm/organizations/{organization_id}/repositories/{repository_id}/pullRequests"
            response = await http_client_service.make_request("get", url, headers, params=params)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                response_data = response.json()
            else:
                response_data = response

            prs_data = response_data.get("data", [])

            pull_requests = []
            for pr_data in prs_data:
                pull_requests.append(PullRequest(**pr_data))

            logger.info(f"Found {len(pull_requests)} pull requests")
            return pull_requests
        except Exception as e:
            logger.error(f"Error getting pull requests: {str(e)}")
            return []

    async def get_pull_request(self, organization_id: str, repository_id: str, pull_request_id: str,
                               integration_id: Optional[str] = None) -> Optional[PullRequest]:
        """Get a specific pull request"""
        logger.info(f"Getting pull request: {pull_request_id} in repository: {repository_id}")
        try:
            headers = extract_headers_from_request()
            if integration_id:
                headers["integrationId"] = integration_id

            url = f"{settings.scm_api_base_url}/api/v1/scm/organizations/{organization_id}/repositories/{repository_id}/pullRequests/{pull_request_id}"
            response = await http_client_service.make_request("get", url, headers)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                pr_data = response.json()
            else:
                pr_data = response

            pull_request = PullRequest(**pr_data)
            logger.info(f"Retrieved pull request: {pull_request_id}")
            return pull_request
        except Exception as e:
            logger.error(f"Error getting pull request {pull_request_id}: {str(e)}")
            return None

    async def create_pull_request(self, organization_id: str, repository_id: str,
                                  pr_request: PullRequestRequest, integration_id: Optional[str] = None) -> Optional[
        PullRequest]:
        """Create a new pull request"""
        logger.info(f"Creating pull request in repository: {repository_id}")
        try:
            headers = extract_headers_from_request()
            if integration_id:
                headers["integrationId"] = integration_id

            url = f"{settings.scm_api_base_url}/api/v1/scm/organizations/{organization_id}/repositories/{repository_id}/pullRequests"
            response = await http_client_service.make_request("post", url, headers, json_data=pr_request.dict())

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                pr_data = response.json()
            else:
                pr_data = response

            pull_request = PullRequest(**pr_data)
            logger.info(f"Created pull request: {pull_request.id}")
            return pull_request
        except Exception as e:
            logger.error(f"Error creating pull request: {str(e)}")
            return None

    async def update_pull_request(self, organization_id: str, repository_id: str, pull_request_id: str,
                                  pr_request: PullRequestRequest, integration_id: Optional[str] = None) -> Optional[
        PullRequest]:
        """Update an existing pull request"""
        logger.info(f"Updating pull request: {pull_request_id} in repository: {repository_id}")
        try:
            headers = extract_headers_from_request()
            if integration_id:
                headers["integrationId"] = integration_id

            url = f"{settings.scm_api_base_url}/api/v1/scm/organizations/{organization_id}/repositories/{repository_id}/pullRequests/{pull_request_id}"
            response = await http_client_service.make_request("put", url, headers, json_data=pr_request.dict())

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                pr_data = response.json()
            else:
                pr_data = response

            pull_request = PullRequest(**pr_data)
            logger.info(f"Updated pull request: {pull_request_id}")
            return pull_request
        except Exception as e:
            logger.error(f"Error updating pull request {pull_request_id}: {str(e)}")
            return None


# Global SCM integration service instance
scm_integration_service = SCMIntegrationService()