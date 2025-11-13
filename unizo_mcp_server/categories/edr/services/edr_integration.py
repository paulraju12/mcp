import structlog
from typing import List, Dict, Any, Optional
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request

logger = structlog.getLogger(__name__)


class EDRIntegrationService:
    """Service for handling EDR API integrations"""

    def __init__(self):
        self.base_url = f"{settings.edr_api_base_url}/api/v1/edr"

    async def get_connectors(self) -> List[dict]:
        """Get list of available EDR connectors"""
        logger.info("Getting list of EDR connectors")
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

            # Filter for EDR type in code
            connectors = []
            seen_connectors = set()
            for integ in integrations:
                # Check if it's a EDR integration
                if integ.get("type") == "EDR" and "serviceProfile" in integ and "name" in integ["serviceProfile"]:
                    connector_name = integ["serviceProfile"]["name"].lower()
                    if connector_name not in seen_connectors:
                        connectors.append({"name": service_name})
                        seen_connectors.add(service_name)

            logger.info(f"Found {len(services)} EDR connectors after filtering")
            return connectors
        except Exception as e:
            logger.error(f"Error getting EDR connectors: {str(e)}")
            return []

    async def get_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific EDR service"""
        logger.info(f"Getting EDR integrations for connector: {service}")
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

            # Filter for EDR type and matching service name in code
            matching_integrations = [
                {"id": integ.get("id"), "name": integ.get("name", "Unnamed Integration")}
                for integ in integrations
                if integ.get("type") == "EDR" and
                   "serviceProfile" in integ and
                   "name" in integ["serviceProfile"] and
                   integ["serviceProfile"]["name"].lower() == connector.lower()
            ]

            logger.info(f"Found {len(matching_integrations)} integrations for EDR connector {connector} after filtering")
            return matching_integrations
        except Exception as e:
            logger.error(f"Error getting EDR integrations: {str(e)}")
            return []

    async def list_devices(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List devices with pagination and sorting"""
        logger.info(f"Listing devices for integration: {integration_id}")
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

            url = f"{self.base_url}/devices"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved devices for integration {integration_id}"
            }

        except Exception as e:
            logger.error(f"Error listing devices: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_device(
            self,
            integration_id: str,
            device_id: str
    ) -> Dict[str, Any]:
        """Get detailed device information"""
        logger.info(f"Getting device {device_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/devices/{device_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved device {device_id}"
            }

        except Exception as e:
            logger.error(f"Error getting device {device_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def list_device_alerts(
            self,
            integration_id: str,
            device_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List alerts for a specific device"""
        logger.info(f"Listing alerts for device {device_id}, integration: {integration_id}")
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

            url = f"{self.base_url}/devices/{device_id}/alerts"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved alerts for device {device_id}"
            }

        except Exception as e:
            logger.error(f"Error listing device alerts: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_device_alert(
            self,
            integration_id: str,
            device_id: str,
            alert_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific device alert"""
        logger.info(f"Getting alert {alert_id} for device {device_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/devices/{device_id}/alerts/{alert_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved alert {alert_id} for device {device_id}"
            }

        except Exception as e:
            logger.error(f"Error getting device alert: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }


# Global EDR integration service instance
edr_integration_service = EDRIntegrationService()