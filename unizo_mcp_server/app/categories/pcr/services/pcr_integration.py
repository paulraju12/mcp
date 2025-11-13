import structlog
from typing import List, Dict, Any, Optional
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request

logger = structlog.getLogger(__name__)


class PCRIntegrationService:
    """Service for handling PCR API integrations"""

    def __init__(self):
        self.base_url = f"{settings.pcr_api_base_url}/api/v1/pcr"

    async def get_connectors(self) -> List[dict]:
        """Get list of available PCR connectors"""
        logger.info("Getting list of PCR connectors")
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

            # Filter for PCR type in code
            connectors = []
            seen_connectors = set()
            for integ in integrations:
                # Check if it's a PCR integration
                if integ.get("type") == "PCR" and "serviceProfile" in integ and "name" in integ["serviceProfile"]:
                    connector_name = integ["serviceProfile"]["name"].lower()
                    if connector_name not in seen_connectors:
                        connectors.append({"name": connector_name})
                        seen_connectors.add(connector_name)

            logger.info(f"Found {len(connectors)} PCR connectors after filtering")
            return connectors
        except Exception as e:
            logger.error(f"Error getting PCR connectors: {str(e)}")
            return []

    async def get_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific PCR connector"""
        logger.info(f"Getting PCR integrations for connector: {connector}")
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

            # Filter for PCR type and matching connector name in code
            matching_integrations = [
                {"id": integ.get("id"), "name": integ.get("name", "Unnamed Integration")}
                for integ in integrations
                if integ.get("type") == "PCR" and
                   "serviceProfile" in integ and
                   "name" in integ["serviceProfile"] and
                   integ["serviceProfile"]["name"].lower() == connector.lower()
            ]

            logger.info(f"Found {len(matching_integrations)} integrations for PCR connector {connector} after filtering")
            return matching_integrations
        except Exception as e:
            logger.error(f"Error getting PCR integrations: {str(e)}")
            return []

    # ---------- ORGANIZATION METHODS ----------
    async def list_organizations(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20
    ) -> Dict[str, Any]:
        """List organizations"""
        logger.info(f"Listing organizations for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }

            url = f"{self.base_url}/organizations"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved organizations for integration {integration_id}"
            }

        except Exception as e:
            logger.error(f"Error listing organizations: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_organization(
            self,
            integration_id: str,
            organization_id: str
    ) -> Dict[str, Any]:
        """Get organization by ID"""
        logger.info(f"Getting organization {organization_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/organizations/{organization_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved organization {organization_id}"
            }

        except Exception as e:
            logger.error(f"Error getting organization {organization_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    # ---------- REPOSITORY METHODS ----------
    async def list_repositories(
            self,
            integration_id: str,
            organization_id: str,
            offset: int = 0,
            limit: int = 20
    ) -> Dict[str, Any]:
        """List repositories for an organization"""
        logger.info(f"Listing repositories for organization {organization_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }

            url = f"{self.base_url}/{organization_id}/repositories"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved repositories for organization {organization_id}"
            }

        except Exception as e:
            logger.error(f"Error listing repositories: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_repository(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str
    ) -> Dict[str, Any]:
        """Get repository by ID"""
        logger.info(f"Getting repository {repository_id} for organization {organization_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/{organization_id}/repositories/{repository_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved repository {repository_id}"
            }

        except Exception as e:
            logger.error(f"Error getting repository {repository_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    # ---------- ARTIFACT METHODS ----------
    async def list_artifacts(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List artifacts for a repository"""
        logger.info(f"Listing artifacts for repository {repository_id}, organization {organization_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }

            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/{organization_id}/repositories/{repository_id}/artifacts"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved artifacts for repository {repository_id}"
            }

        except Exception as e:
            logger.error(f"Error listing artifacts: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_artifact(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str,
            artifact_id: str
    ) -> Dict[str, Any]:
        """Get artifact by ID"""
        logger.info(f"Getting artifact {artifact_id} for repository {repository_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/{organization_id}/repositories/{repository_id}/artifacts/{artifact_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved artifact {artifact_id}"
            }

        except Exception as e:
            logger.error(f"Error getting artifact {artifact_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    # ---------- TAG METHODS ----------
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
        """List tags for an artifact"""
        logger.info(f"Listing tags for artifact {artifact_id}, repository {repository_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }

            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/{organization_id}/repositories/{repository_id}/artifacts/{artifact_id}/tags"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved tags for artifact {artifact_id}"
            }

        except Exception as e:
            logger.error(f"Error listing tags: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_tag(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str,
            artifact_id: str,
            tag_id: str
    ) -> Dict[str, Any]:
        """Get tag by ID"""
        logger.info(f"Getting tag {tag_id} for artifact {artifact_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/{organization_id}/repositories/{repository_id}/artifacts/{artifact_id}/tags/{tag_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved tag {tag_id}"
            }

        except Exception as e:
            logger.error(f"Error getting tag {tag_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }


# Global PCR integration service instance
pcr_integration_service = PCRIntegrationService()