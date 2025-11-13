import structlog
from typing import List, Dict, Any, Optional
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request

logger = structlog.getLogger(__name__)


class ObservabilityIntegrationService:
    """Service for handling Observability API integrations"""

    def __init__(self):
        self.base_url = f"{settings.observability_api_base_url}/api/v1"

    async def get_connectors(self) -> List[dict]:
        """Get list of available OBSERVABILITY connectors"""
        logger.info("Getting list of OBSERVABILITY connectors")
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

            # Filter for OBSERVABILITY type in code
            connectors = []
            seen_connectors = set()
            for integ in integrations:
                # Check if it's a OBSERVABILITY integration
                if integ.get("type") == "OBSERVABILITY" and "serviceProfile" in integ and "name" in integ["serviceProfile"]:
                    connector_name = integ["serviceProfile"]["name"].lower()
                    if connector_name not in seen_connectors:
                        connectors.append({"name": connector_name})
                        seen_connectors.add(connector_name)

            logger.info(f"Found {len(connectors)} OBSERVABILITY connectors after filtering")
            return connectors
        except Exception as e:
            logger.error(f"Error getting OBSERVABILITY connectors: {str(e)}")
            return []

    async def get_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific OBSERVABILITY connector"""
        logger.info(f"Getting OBSERVABILITY integrations for connector: {connector}")
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

            # Filter for OBSERVABILITY type and matching connector name in code
            matching_integrations = [
                {"id": integ.get("id"), "name": integ.get("name", "Unnamed Integration")}
                for integ in integrations
                if integ.get("type") == "OBSERVABILITY" and
                   "serviceProfile" in integ and
                   "name" in integ["serviceProfile"] and
                   integ["serviceProfile"]["name"].lower() == connector.lower()
            ]

            logger.info(f"Found {len(matching_integrations)} integrations for OBSERVABILITY connector {connector} after filtering")
            return matching_integrations
        except Exception as e:
            logger.error(f"Error getting OBSERVABILITY integrations: {str(e)}")
            return []

    async def list_logs(
            self,
            integration_id: str,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List logs with filtering and pagination"""
        logger.info(f"Listing logs for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            params = {}

            # Add optional query parameters
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/logs"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved logs for integration {integration_id}"
            }

        except Exception as e:
            logger.error(f"Error listing logs: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_log(
            self,
            integration_id: str,
            log_id: str
    ) -> Dict[str, Any]:
        """Get detailed log information"""
        logger.info(f"Getting log {log_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{self.base_url}/logs/{log_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved log {log_id}"
            }

        except Exception as e:
            logger.error(f"Error getting log {log_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }


# Global observability integration service instance
observability_integration_service = ObservabilityIntegrationService()