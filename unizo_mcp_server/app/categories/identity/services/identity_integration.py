import structlog
from typing import List, Dict, Any, Optional
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request

logger = structlog.getLogger(__name__)


class IdentityIntegrationService:
    """Service for handling Identity API integrations"""

    def __init__(self):
        self.base_url = f"{settings.identity_api_base_url}/api/v1/identity"

    async def get_connectors(self) -> List[dict]:
        """Get list of available IDENTITY connectors"""
        logger.info("Getting list of IDENTITY connectors")
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

            # Filter for IDENTITY type in code
            connectors = []
            seen_connectors = set()
            for integ in integrations:
                # Check if it's a IDENTITY integration
                if integ.get("type") == "IDENTITY" and "serviceProfile" in integ and "name" in integ["serviceProfile"]:
                    connector_name = integ["serviceProfile"]["name"].lower()
                    if connector_name not in seen_connectors:
                        connectors.append({"name": connector_name})
                        seen_connectors.add(connector_name)

            logger.info(f"Found {len(connectors)} IDENTITY connectors after filtering")
            return connectors
        except Exception as e:
            logger.error(f"Error getting IDENTITY connectors: {str(e)}")
            return []

    async def get_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific IDENTITY connector"""
        logger.info(f"Getting IDENTITY integrations for connector: {connector}")
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

            # Filter for IDENTITY type and matching service name in code
            matching_integrations = [
                {"id": integ.get("id"), "name": integ.get("name", "Unnamed Integration")}
                for integ in integrations
                if integ.get("type") == "IDENTITY" and
                   "serviceProfile" in integ and
                   "name" in integ["serviceProfile"] and
                   integ["serviceProfile"]["name"].lower() == connector.lower()
            ]

            logger.info(f"Found {len(matching_integrations)} integrations for IDENTITY connector {connector} after filtering")
            return matching_integrations
        except Exception as e:
            logger.error(f"Error getting IDENTITY integrations: {str(e)}")
            return []

    async def list_users(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            status: Optional[str] = None,
            mfa_status: Optional[str] = None,
            user_type: Optional[str] = None,
            search: Optional[str] = None,
            domain: Optional[str] = None,
            has_devices: Optional[bool] = None,
            last_login_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """List users with filtering and pagination"""
        logger.info(f"Listing users for integration: {integration_id}")
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
            if status:
                params["status"] = status
            if mfa_status:
                params["mfaStatus"] = mfa_status
            if user_type:
                params["userType"] = user_type
            if search:
                params["search"] = search
            if domain:
                params["domain"] = domain
            if has_devices is not None:
                params["hasDevices"] = has_devices
            if last_login_days:
                params["lastLoginDays"] = last_login_days

            url = f"{self.base_url}/users"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved users for integration {integration_id}"
            }

        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_user(
            self,
            integration_id: str,
            user_id: str,
            expand: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get detailed user information"""
        logger.info(f"Getting user {user_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {}
            if expand:
                params["expand"] = expand

            url = f"{self.base_url}/users/{user_id}"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved user {user_id}"
            }

        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def list_groups(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            group_type: Optional[str] = None,
            status: Optional[str] = None,
            search: Optional[str] = None,
            has_members: Optional[bool] = None,
            parent_group_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List groups with filtering and pagination"""
        logger.info(f"Listing groups for integration: {integration_id}")
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
            if group_type:
                params["groupType"] = group_type
            if status:
                params["status"] = status
            if search:
                params["search"] = search
            if has_members is not None:
                params["hasMembers"] = has_members
            if parent_group_id:
                params["parentGroupId"] = parent_group_id

            url = f"{self.base_url}/groups"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved groups for integration {integration_id}"
            }

        except Exception as e:
            logger.error(f"Error listing groups: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_group(
            self,
            integration_id: str,
            group_id: str,
            expand: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get detailed group information"""
        logger.info(f"Getting group {group_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {}
            if expand:
                params["expand"] = expand

            url = f"{self.base_url}/groups/{group_id}"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved group {group_id}"
            }

        except Exception as e:
            logger.error(f"Error getting group {group_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def list_group_members(
            self,
            integration_id: str,
            group_id: str,
            offset: int = 0,
            limit: int = 20,
            member_type: Optional[str] = None,
            status: Optional[str] = None,
            search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List members of a specific group"""
        logger.info(f"Listing members for group {group_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }

            # Add optional query parameters
            if member_type:
                params["memberType"] = member_type
            if status:
                params["status"] = status
            if search:
                params["search"] = search

            url = f"{self.base_url}/groups/{group_id}/members"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved members for group {group_id}"
            }

        except Exception as e:
            logger.error(f"Error listing group members: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_group_member(
            self,
            integration_id: str,
            group_id: str,
            member_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific group member"""
        logger.info(f"Getting member {member_id} for group {group_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/groups/{group_id}/members/{member_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved member {member_id} from group {group_id}"
            }

        except Exception as e:
            logger.error(f"Error getting group member: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def list_user_sessions(
            self,
            integration_id: str,
            user_id: str,
            status: str = "active",
            offset: int = 0,
            limit: int = 20,
            from_date: Optional[str] = None,
            to_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """List sessions for a specific user"""
        logger.info(f"Listing sessions for user {user_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {
                "status": status,
                "offset": offset,
                "limit": limit
            }

            # Add optional query parameters
            if from_date:
                params["from"] = from_date
            if to_date:
                params["to"] = to_date

            url = f"{self.base_url}/users/{user_id}/sessions"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved sessions for user {user_id}"
            }

        except Exception as e:
            logger.error(f"Error listing user sessions: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_user_session(
            self,
            integration_id: str,
            user_id: str,
            session_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific session"""
        logger.info(f"Getting session {session_id} for user {user_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/users/{user_id}/sessions/{session_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved session {session_id} for user {user_id}"
            }

        except Exception as e:
            logger.error(f"Error getting user session: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def list_audit_logs(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            since: Optional[str] = None,
            log_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """List audit logs with filtering and pagination"""
        logger.info(f"Listing audit logs for integration: {integration_id}")
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
            if since:
                params["since"] = since
            if log_type:
                params["type"] = log_type

            url = f"{self.base_url}/logs"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved audit logs for integration {integration_id}"
            }

        except Exception as e:
            logger.error(f"Error listing audit logs: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def get_audit_log(
            self,
            integration_id: str,
            audit_log_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific audit log"""
        logger.info(f"Getting audit log {audit_log_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/logs/{audit_log_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved audit log {audit_log_id}"
            }

        except Exception as e:
            logger.error(f"Error getting audit log {audit_log_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }


# Global identity integration service instance
identity_integration_service = IdentityIntegrationService()