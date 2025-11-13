import structlog
from typing import List, Dict, Any, Optional
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request

logger = structlog.getLogger(__name__)


class VMSIntegrationService:
    """Service for handling VMS API integrations"""

    def __init__(self):
        self.base_url = f"{settings.vms_api_base_url}/api/v1/vms"
        self.DEFAULT_ASSET_ID = "default"

    async def get_connectors(self) -> List[dict]:
        """Get list of available VMS connectors"""
        logger.info("Getting list of VMS connectors")
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

            # Filter for VMS type in code
            connectors = []
            seen_connectors = set()
            for integ in integrations:
                # Check if it's a VMS integration
                if integ.get("type") == "VMS" and "serviceProfile" in integ and "name" in integ["serviceProfile"]:
                    connector_name = integ["serviceProfile"]["name"].lower()
                    if connector_name not in seen_connectors:
                        connectors.append({"name": connector_name})
                        seen_connectors.add(connector_name)

            logger.info(f"Found {len(connectors)} VMS connectors after filtering")
            return connectors
        except Exception as e:
            logger.error(f"Error getting VMS connectors: {str(e)}")
            return []

    async def get_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific VMS connector"""
        logger.info(f"Getting VMS integrations for connector: {connector}")
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

            # Filter for VMS type and matching connector name in code
            matching_integrations = [
                {"id": integ.get("id"), "name": integ.get("name", "Unnamed Integration")}
                for integ in integrations
                if integ.get("type") == "VMS" and
                   "serviceProfile" in integ and
                   "name" in integ["serviceProfile"] and
                   integ["serviceProfile"]["name"].lower() == connector.lower()
            ]

            logger.info(f"Found {len(matching_integrations)} integrations for VMS connector {connector} after filtering")
            return matching_integrations
        except Exception as e:
            logger.error(f"Error getting VMS integrations: {str(e)}")
            return []

    async def _check_provider_supports_assets(self, integration_id: str) -> bool:
        """Check if the provider supports assets by trying to list assets."""
        try:
            result = await self.list_assets(integration_id=integration_id, offset=0, limit=1)
            if result["status"] == "success":
                return True
            return False
        except Exception as e:
            logger.warning(f"Provider {integration_id} does not support assets: {str(e)}")
            return False

    async def _get_effective_asset_id(self, integration_id: str, asset_id: Optional[str] = None) -> str:
        """Get the effective asset ID to use for API calls."""
        if asset_id:
            return asset_id

        # Check if provider supports assets
        supports_assets = await self._check_provider_supports_assets(integration_id)
        if not supports_assets:
            logger.info(f"Provider {integration_id} doesn't support assets, using default asset ID")
            return self.DEFAULT_ASSET_ID

        # Try to get first asset if available
        assets_result = await self.list_assets(integration_id=integration_id, limit=1)
        if assets_result["status"] == "success":
            assets_data = assets_result["data"].get("data", [])
            if assets_data:
                first_asset_id = assets_data[0].get("id")
                if first_asset_id:
                    return first_asset_id

        # Fallback to default
        return self.DEFAULT_ASSET_ID

    # ---------- VULNERABILITY OPERATIONS ----------
    async def list_vulnerabilities(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            asset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List vulnerabilities using asset-based endpoint"""
        logger.info(f"Listing vulnerabilities for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            # Get effective asset ID
            effective_asset_id = await self._get_effective_asset_id(integration_id, asset_id)

            params = {
                "offset": offset,
                "limit": limit
            }

            if sort:
                params["sort"] = sort

            # Use new asset-based endpoint
            url = f"{self.base_url}/assets/{effective_asset_id}/vulnerabilities"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved vulnerabilities for asset {effective_asset_id} in integration {integration_id}"
            }

        except Exception as e:
            logger.error(f"Error listing vulnerabilities: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def list_assets(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List assets with pagination and sorting"""
        logger.info(f"Listing assets for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }

            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/assets"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved assets for integration {integration_id}"
            }

        except Exception as e:
            logger.error(f"Error listing assets: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def list_scans(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            asset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List scans using asset-based endpoint"""
        logger.info(f"Listing scans for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            # Get effective asset ID
            effective_asset_id = await self._get_effective_asset_id(integration_id, asset_id)

            params = {
                "offset": offset,
                "limit": limit
            }

            if sort:
                params["sort"] = sort

            # Use new asset-based endpoint
            url = f"{self.base_url}/assets/{effective_asset_id}/scans"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved scans for asset {effective_asset_id} in integration {integration_id}"
            }

        except Exception as e:
            logger.error(f"Error listing scans: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }


# Global VMS integration service instance
vms_integration_service = VMSIntegrationService()