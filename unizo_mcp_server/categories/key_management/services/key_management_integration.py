import structlog
from typing import List, Dict, Any, Optional
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request
from ..models.key_management_models import (
    VaultConfigRequest
)

logger = structlog.getLogger(__name__)


class KeyManagementIntegrationService:
    """Service for handling Key Management API integrations"""

    def __init__(self):
        self.base_url = f"{settings.key_management_api_base_url}/api/v1"

    async def get_connectors(self) -> List[dict]:
        """Get list of available KEY_MANAGEMENT connectors"""
        logger.info("Getting list of KEY_MANAGEMENT connectors")
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

            # Filter for KEY_MANAGEMENT type in code
            connectors = []
            seen_connectors = set()
            for integ in integrations:
                # Check if it's a KEY_MANAGEMENT integration
                if integ.get("type") == "KEY_MANAGEMENT" and "serviceProfile" in integ and "name" in integ["serviceProfile"]:
                    connector_name = integ["serviceProfile"]["name"].lower()
                    if connector_name not in seen_connectors:
                        connectors.append({"name": connector_name})
                        seen_connectors.add(connector_name)

            logger.info(f"Found {len(connectors)} KEY_MANAGEMENT connectors after filtering")
            return connectors
        except Exception as e:
            logger.error(f"Error getting KEY_MANAGEMENT connectors: {str(e)}")
            return []

    async def get_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific KEY_MANAGEMENT connector"""
        logger.info(f"Getting KEY_MANAGEMENT integrations for connector: {connector}")
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

            # Filter for KEY_MANAGEMENT type and matching connector name in code
            matching_integrations = [
                {"id": integ.get("id"), "name": integ.get("name", "Unnamed Integration")}
                for integ in integrations
                if integ.get("type") == "KEY_MANAGEMENT" and
                   "serviceProfile" in integ and
                   "name" in integ["serviceProfile"] and
                   integ["serviceProfile"]["name"].lower() == connector.lower()
            ]

            logger.info(f"Found {len(matching_integrations)} integrations for KEY_MANAGEMENT connector {connector} after filtering")
            return matching_integrations
        except Exception as e:
            logger.error(f"Error getting KEY_MANAGEMENT integrations: {str(e)}")
            return []

    async def list_vault_configs(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List vault configurations with filtering and pagination"""
        logger.info(f"Listing vault configurations for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }

            # Add optional query parameters
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/vaultConfigs"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved vault configurations for integration {integration_id}"
            }

        except Exception as e:
            logger.error(f"Error listing vault configurations: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_vault_config(
            self,
            integration_id: str,
            vault_config_id: str
    ) -> Dict[str, Any]:
        """Get detailed vault configuration information"""
        logger.info(f"Getting vault configuration {vault_config_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/vaultConfigs/{vault_config_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved vault configuration {vault_config_id}"
            }

        except Exception as e:
            logger.error(f"Error getting vault configuration {vault_config_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def create_vault_config(
            self,
            integration_id: str,
            vault_config_request: VaultConfigRequest
    ) -> Dict[str, Any]:
        """Create a new vault configuration"""
        logger.info(f"Creating vault configuration for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/vaultConfigs"
            response = await http_client_service.make_request(
                "post",
                url,
                headers,
                json_data=vault_config_request.dict()
            )

            return {
                "status": "success",
                "data": response,
                "message": f"Created vault configuration for integration {integration_id}"
            }

        except Exception as e:
            logger.error(f"Error creating vault configuration: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }


# Global key management integration service instance
key_management_integration_service = KeyManagementIntegrationService()