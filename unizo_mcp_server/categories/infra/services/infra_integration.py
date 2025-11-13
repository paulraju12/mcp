import structlog
from typing import List, Dict, Any, Optional
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request

logger = structlog.getLogger(__name__)


class InfraIntegrationService:
    """Service for handling Infrastructure API integrations"""

    def __init__(self):
        self.base_url = f"{settings.infra_api_base_url}/api/v1/infra"

    async def get_connectors(self) -> List[dict]:
        """Get list of available INFRA connectors"""
        logger.info("Getting list of INFRA connectors")
        try:
            headers = extract_headers_from_request()

            # Build filter - ONLY organization/suborganization filter
            filter_conditions = []

            # Check for suborganizationId first
            suborganization_id = headers.get("suborganizationId")
            organization_id = headers.get("organizationId")

            if suborganization_id:
                filter_conditions.append({
                    "property": "/subOrganization/externalKey",
                    "operator": "=",
                    "values": [suborganization_id]
                })
                logger.info(f"Filtering by subOrganization/externalKey: {suborganization_id}")
            elif organization_id:
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

            # Filter for INFRA type in code
            connectors = []
            seen_connectors = set()
            for integ in integrations:
                if integ.get("type") == "INFRA" and "serviceProfile" in integ and "name" in integ["serviceProfile"]:
                    connector_name = integ["serviceProfile"]["name"].lower()
                    if connector_name not in seen_connectors:
                        connectors.append({"name": connector_name})
                        seen_connectors.add(connector_name)

            logger.info(f"Found {len(connectors)} INFRA connectors after filtering")
            return connectors
        except Exception as e:
            logger.error(f"Error getting INFRA connectors: {str(e)}")
            return []

    async def get_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific INFRA connector"""
        logger.info(f"Getting INFRA integrations for connector: {connector}")
        try:
            headers = extract_headers_from_request()

            # Build filter - ONLY organization/suborganization filter
            filter_conditions = []

            suborganization_id = headers.get("suborganizationId")
            organization_id = headers.get("organizationId")

            if suborganization_id:
                filter_conditions.append({
                    "property": "/subOrganization/externalKey",
                    "operator": "=",
                    "values": [suborganization_id]
                })
                logger.info(f"Filtering by subOrganization/externalKey: {suborganization_id}")
            elif organization_id:
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

            # Filter for INFRA type and matching connector name in code
            matching_integrations = [
                {"id": integ.get("id"), "name": integ.get("name", "Unnamed Integration")}
                for integ in integrations
                if integ.get("type") == "INFRA" and
                   "serviceProfile" in integ and
                   "name" in integ["serviceProfile"] and
                   integ["serviceProfile"]["name"].lower() == connector.lower()
            ]

            logger.info(f"Found {len(matching_integrations)} integrations for INFRA connector {connector} after filtering")
            return matching_integrations
        except Exception as e:
            logger.error(f"Error getting INFRA integrations: {str(e)}")
            return []

    # ========== ACCOUNT METHODS ==========
    async def list_accounts(
            self,
            integration_id: str,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List accounts"""
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {}
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/accounts"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved accounts for integration {integration_id}"
            }
        except Exception as e:
            logger.error(f"Error listing accounts: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_account(
            self,
            integration_id: str,
            account_id: str
    ) -> Dict[str, Any]:
        """Get account by ID"""
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/accounts/{account_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved account {account_id}"
            }
        except Exception as e:
            logger.error(f"Error getting account {account_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    # ========== COLLECTION METHODS ==========
    async def list_collections(
            self,
            integration_id: str,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List collections"""
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {}
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/collections"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved collections for integration {integration_id}"
            }
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_collection(
            self,
            integration_id: str,
            collection_id: str
    ) -> Dict[str, Any]:
        """Get collection by ID"""
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/collections/{collection_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved collection {collection_id}"
            }
        except Exception as e:
            logger.error(f"Error getting collection {collection_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    # ========== USER METHODS ==========
    async def list_users(
            self,
            integration_id: str,
            collection_id: str,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List users in a collection"""
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {}
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/collections/{collection_id}/users"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved users for collection {collection_id}"
            }
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_user(
            self,
            integration_id: str,
            collection_id: str,
            user_id: str
    ) -> Dict[str, Any]:
        """Get user by ID"""
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/collections/{collection_id}/users/{user_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved user {user_id}"
            }
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    # ========== RESOURCE METHODS ==========
    async def list_resources(
            self,
            integration_id: str,
            collection_id: str,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None,
            parent_resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List resources in a collection"""
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {}
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if sort:
                params["sort"] = sort
            if parent_resource_id:
                params["parentResourceId"] = parent_resource_id

            url = f"{self.base_url}/collections/{collection_id}/resources"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved resources for collection {collection_id}"
            }
        except Exception as e:
            logger.error(f"Error listing resources: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_resource(
            self,
            integration_id: str,
            collection_id: str,
            resource_id: str,
            parent_resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get resource by ID"""
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {}
            if parent_resource_id:
                params["parentResourceId"] = parent_resource_id

            url = f"{self.base_url}/collections/{collection_id}/resources/{resource_id}"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved resource {resource_id}"
            }
        except Exception as e:
            logger.error(f"Error getting resource {resource_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    # ========== POLICY METHODS ==========
    async def list_policies(
            self,
            integration_id: str,
            collection_id: str,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List policies in a collection"""
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {}
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/collections/{collection_id}/policies"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved policies for collection {collection_id}"
            }
        except Exception as e:
            logger.error(f"Error listing policies: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_policy(
            self,
            integration_id: str,
            collection_id: str,
            policy_id: str
    ) -> Dict[str, Any]:
        """Get policy by ID"""
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/collections/{collection_id}/policies/{policy_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved policy {policy_id}"
            }
        except Exception as e:
            logger.error(f"Error getting policy {policy_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    # ========== ROLE METHODS ==========
    async def list_roles(
            self,
            integration_id: str,
            collection_id: str,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List roles in a collection"""
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {}
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/collections/{collection_id}/roles"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved roles for collection {collection_id}"
            }
        except Exception as e:
            logger.error(f"Error listing roles: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_role(
            self,
            integration_id: str,
            collection_id: str,
            role_id: str
    ) -> Dict[str, Any]:
        """Get role by ID"""
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/collections/{collection_id}/roles/{role_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved role {role_id}"
            }
        except Exception as e:
            logger.error(f"Error getting role {role_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}


# Global infrastructure integration service instance
infra_integration_service = InfraIntegrationService()