import structlog
from typing import List, Dict, Any, Optional
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request
from ..models.comms_models import (
    MessageRequest
)

logger = structlog.getLogger(__name__)


class CommsIntegrationService:
    """Service for handling Communications API integrations"""

    def __init__(self):
        self.base_url = f"{settings.comms_api_base_url}/api/v1/comms"

    async def get_connectors(self) -> List[dict]:
        """Get list of available COMMS connectors"""
        logger.info("Getting list of COMMS connectors")
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

            # Filter for COMMS type in code
            connectors = []
            seen_connectors = set()
            for integ in integrations:
                # Check if it's a COMMS integration
                if integ.get("type") == "COMMS" and "serviceProfile" in integ and "name" in integ["serviceProfile"]:
                    connector_name = integ["serviceProfile"]["name"].lower()
                    if connector_name not in seen_connectors:
                        connectors.append({"name": service_name})
                        seen_connectors.add(service_name)

            logger.info(f"Found {len(services)} COMMS connectors after filtering")
            return connectors
        except Exception as e:
            logger.error(f"Error getting COMMS connectors: {str(e)}")
            return []

    async def get_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific COMMS service"""
        logger.info(f"Getting COMMS integrations for connector: {service}")
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

            # Filter for COMMS type and matching service name in code
            matching_integrations = [
                {"id": integ.get("id"), "name": integ.get("name", "Unnamed Integration")}
                for integ in integrations
                if integ.get("type") == "COMMS" and
                   "serviceProfile" in integ and
                   "name" in integ["serviceProfile"] and
                   integ["serviceProfile"]["name"].lower() == connector.lower()
            ]

            logger.info(f"Found {len(matching_integrations)} integrations for COMMS connector {connector} after filtering")
            return matching_integrations
        except Exception as e:
            logger.error(f"Error getting COMMS integrations: {str(e)}")
            return []

    async def list_organizations(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List organizations with pagination"""
        logger.info(f"Listing organizations for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }

            if sort:
                params["sort"] = sort

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
        """Get detailed organization information"""
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

    async def list_channels(
            self,
            integration_id: str,
            organization_id: str,
            parent_id: Optional[str] = None,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List channels for an organization"""
        logger.info(f"Listing channels for organization {organization_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }

            if parent_id:
                params["parentId"] = parent_id
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/{organization_id}/channels"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved channels for organization {organization_id}"
            }

        except Exception as e:
            logger.error(f"Error listing channels: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_channel(
            self,
            integration_id: str,
            organization_id: str,
            channel_id: str
    ) -> Dict[str, Any]:
        """Get detailed channel information"""
        logger.info(f"Getting channel {channel_id} for organization {organization_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/{organization_id}/channels/{channel_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved channel {channel_id}"
            }

        except Exception as e:
            logger.error(f"Error getting channel {channel_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def create_message(
            self,
            integration_id: str,
            organization_id: str,
            channel_id: str,
            message_data: MessageRequest
    ) -> Dict[str, Any]:
        """Create a new message in a channel"""
        logger.info(f"Creating message in channel {channel_id}, organization {organization_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/{organization_id}/channels/{channel_id}/messages"
            response = await http_client_service.make_request(
                "post",
                url,
                headers,
                json_data=message_data.dict(exclude_unset=True)
            )

            return {
                "status": "success",
                "data": response,
                "message": f"Message created successfully in channel {channel_id}"
            }

        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }


# Global communications integration service instance
comms_integration_service = CommsIntegrationService()