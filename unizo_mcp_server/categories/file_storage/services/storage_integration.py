import structlog
from typing import List, Dict, Any, Optional
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request

logger = structlog.getLogger(__name__)


class StorageIntegrationService:
    """Service for handling File Storage API integrations"""

    def __init__(self):
        self.base_url = f"{settings.storage_api_base_url}/api/v1/storage"

    async def get_connectors(self) -> List[dict]:
        """Get list of available STORAGE connectors"""
        logger.info("Getting list of STORAGE connectors")
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

            # Filter for STORAGE type in code
            connectors = []
            seen_connectors = set()
            for integ in integrations:
                if integ.get("type") == "STORAGE" and "serviceProfile" in integ and "name" in integ["serviceProfile"]:
                    connector_name = integ["serviceProfile"]["name"].lower()
                    if connector_name not in seen_connectors:
                        connectors.append({"name": connector_name})
                        seen_connectors.add(connector_name)

            logger.info(f"Found {len(connectors)} STORAGE connectors after filtering")
            return connectors
        except Exception as e:
            logger.error(f"Error getting STORAGE connectors: {str(e)}")
            return []

    async def get_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific STORAGE connector"""
        logger.info(f"Getting STORAGE integrations for connector: {connector}")
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

            # Filter for STORAGE type and matching connector name in code
            matching_integrations = [
                {"id": integ.get("id"), "name": integ.get("name", "Unnamed Integration")}
                for integ in integrations
                if integ.get("type") == "STORAGE" and
                   "serviceProfile" in integ and
                   "name" in integ["serviceProfile"] and
                   integ["serviceProfile"]["name"].lower() == connector.lower()
            ]

            logger.info(
                f"Found {len(matching_integrations)} integrations for STORAGE connector {connector} after filtering")
            return matching_integrations
        except Exception as e:
            logger.error(f"Error getting STORAGE integrations: {str(e)}")
            return []

    # ---------- DRIVE OPERATIONS ----------
    async def list_drives(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List drives"""
        logger.info(f"Listing drives for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {"offset": offset, "limit": limit}
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/drives"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved drives for integration {integration_id}"
            }
        except Exception as e:
            logger.error(f"Error listing drives: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_drive(self, integration_id: str, drive_id: str) -> Dict[str, Any]:
        """Get drive details"""
        logger.info(f"Getting drive {drive_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/drives/{drive_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved drive {drive_id}"
            }
        except Exception as e:
            logger.error(f"Error getting drive {drive_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    # ---------- FOLDER OPERATIONS ----------
    async def list_folders(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List folders"""
        logger.info(f"Listing folders for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {"offset": offset, "limit": limit}
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/folders"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved folders for integration {integration_id}"
            }
        except Exception as e:
            logger.error(f"Error listing folders: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_folder(self, integration_id: str, folder_id: str) -> Dict[str, Any]:
        """Get folder details"""
        logger.info(f"Getting folder {folder_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/folders/{folder_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved folder {folder_id}"
            }
        except Exception as e:
            logger.error(f"Error getting folder {folder_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def create_folder(self, integration_id: str, folder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new folder"""
        logger.info(f"Creating folder for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/folders"
            response = await http_client_service.make_request("post", url, headers, json_data=folder_data)

            return {
                "status": "success",
                "data": response,
                "message": "Folder created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def update_folder(self, integration_id: str, folder_id: str, folder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing folder"""
        logger.info(f"Updating folder {folder_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/folders/{folder_id}"
            response = await http_client_service.make_request("put", url, headers, json_data=folder_data)

            return {
                "status": "success",
                "data": response,
                "message": f"Folder {folder_id} updated successfully"
            }
        except Exception as e:
            logger.error(f"Error updating folder {folder_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def delete_folder(self, integration_id: str, folder_id: str) -> Dict[str, Any]:
        """Delete a folder"""
        logger.info(f"Deleting folder {folder_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/folders/{folder_id}"
            response = await http_client_service.make_request("delete", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Folder {folder_id} deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting folder {folder_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    # ---------- FILE OPERATIONS ----------
    async def list_files(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List files"""
        logger.info(f"Listing files for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {"offset": offset, "limit": limit}
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/files"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved files for integration {integration_id}"
            }
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_file(self, integration_id: str, file_id: str) -> Dict[str, Any]:
        """Get file details"""
        logger.info(f"Getting file {file_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/files/{file_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved file {file_id}"
            }
        except Exception as e:
            logger.error(f"Error getting file {file_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def create_file(self, integration_id: str, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new file"""
        logger.info(f"Creating file for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/files"
            response = await http_client_service.make_request("post", url, headers, json_data=file_data)

            return {
                "status": "success",
                "data": response,
                "message": "File created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating file: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def update_file(self, integration_id: str, file_id: str, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing file"""
        logger.info(f"Updating file {file_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/files/{file_id}"
            response = await http_client_service.make_request("put", url, headers, json_data=file_data)

            return {
                "status": "success",
                "data": response,
                "message": f"File {file_id} updated successfully"
            }
        except Exception as e:
            logger.error(f"Error updating file {file_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def delete_file(self, integration_id: str, file_id: str) -> Dict[str, Any]:
        """Delete a file"""
        logger.info(f"Deleting file {file_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/files/{file_id}"
            response = await http_client_service.make_request("delete", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"File {file_id} deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    # ---------- USER OPERATIONS ----------
    async def list_users(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List users"""
        logger.info(f"Listing users for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {"offset": offset, "limit": limit}
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/users"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved users for integration {integration_id}"
            }
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_user(self, integration_id: str, user_id: str) -> Dict[str, Any]:
        """Get user details"""
        logger.info(f"Getting user {user_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/users/{user_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved user {user_id}"
            }
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    # ---------- GROUP OPERATIONS ----------
    async def list_groups(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List groups"""
        logger.info(f"Listing groups for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {"offset": offset, "limit": limit}
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/groups"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved groups for integration {integration_id}"
            }
        except Exception as e:
            logger.error(f"Error listing groups: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_group(self, integration_id: str, group_id: str) -> Dict[str, Any]:
        """Get group details"""
        logger.info(f"Getting group {group_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/groups/{group_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved group {group_id}"
            }
        except Exception as e:
            logger.error(f"Error getting group {group_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    # ---------- VERSION OPERATIONS (FIXED) ----------
    async def list_versions(
            self,
            integration_id: str,
            file_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List file versions"""
        logger.info(f"Listing versions for file {file_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {"offset": offset, "limit": limit}
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/files/{file_id}/versions"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved versions for file {file_id}"
            }
        except Exception as e:
            logger.error(f"Error listing versions: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_version(self, integration_id: str, file_id: str, version_id: str) -> Dict[str, Any]:
        """Get version details"""
        logger.info(f"Getting version {version_id} for file {file_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/files/{file_id}/versions/{version_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved version {version_id}"
            }
        except Exception as e:
            logger.error(f"Error getting version {version_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    # ---------- PERMISSION OPERATIONS (FIXED) ----------
    async def list_permissions(
            self,
            integration_id: str,
            file_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List file permissions"""
        logger.info(f"Listing permissions for file {file_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {"offset": offset, "limit": limit}
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/files/{file_id}/permissions"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved permissions for file {file_id}"
            }
        except Exception as e:
            logger.error(f"Error listing permissions: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_permission(self, integration_id: str, file_id: str, permission_id: str) -> Dict[str, Any]:
        """Get permission details"""
        logger.info(f"Getting permission {permission_id} for file {file_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/files/{file_id}/permissions/{permission_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved permission {permission_id}"
            }
        except Exception as e:
            logger.error(f"Error getting permission {permission_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def add_permission(self, integration_id: str, file_id: str, permission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new permission"""
        logger.info(f"Adding permission for file {file_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/files/{file_id}/permissions"
            response = await http_client_service.make_request("post", url, headers, json_data=permission_data)

            return {
                "status": "success",
                "data": response,
                "message": "Permission added successfully"
            }
        except Exception as e:
            logger.error(f"Error adding permission: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def delete_permission(self, integration_id: str, file_id: str, permission_id: str) -> Dict[str, Any]:
        """Delete a permission"""
        logger.info(f"Deleting permission {permission_id} for file {file_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/files/{file_id}/permissions/{permission_id}"
            response = await http_client_service.make_request("delete", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Permission {permission_id} deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting permission {permission_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    # ---------- COMMENT OPERATIONS (FIXED) ----------
    async def list_comments(
            self,
            integration_id: str,
            file_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List file comments"""
        logger.info(f"Listing comments for file {file_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            params = {"offset": offset, "limit": limit}
            if sort:
                params["sort"] = sort

            url = f"{self.base_url}/files/{file_id}/comments"
            response = await http_client_service.make_request("get", url, headers, params=params)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved comments for file {file_id}"
            }
        except Exception as e:
            logger.error(f"Error listing comments: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def get_comment(self, integration_id: str, file_id: str, comment_id: str) -> Dict[str, Any]:
        """Get comment details"""
        logger.info(f"Getting comment {comment_id} for file {file_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/files/{file_id}/comments/{comment_id}"
            response = await http_client_service.make_request("get", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Retrieved comment {comment_id}"
            }
        except Exception as e:
            logger.error(f"Error getting comment {comment_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def create_comment(self, integration_id: str, file_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new comment"""
        logger.info(f"Creating comment for file {file_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/files/{file_id}/comments"
            response = await http_client_service.make_request("post", url, headers, json_data=comment_data)

            return {
                "status": "success",
                "data": response,
                "message": "Comment created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def update_comment(self, integration_id: str, file_id: str, comment_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing comment"""
        logger.info(f"Updating comment {comment_id} for file {file_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/files/{file_id}/comments/{comment_id}"
            response = await http_client_service.make_request("put", url, headers, json_data=comment_data)

            return {
                "status": "success",
                "data": response,
                "message": f"Comment {comment_id} updated successfully"
            }
        except Exception as e:
            logger.error(f"Error updating comment {comment_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}

    async def delete_comment(self, integration_id: str, file_id: str, comment_id: str) -> Dict[str, Any]:
        """Delete a comment"""
        logger.info(f"Deleting comment {comment_id} for file {file_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{self.base_url}/files/{file_id}/comments/{comment_id}"
            response = await http_client_service.make_request("delete", url, headers)

            return {
                "status": "success",
                "data": response,
                "message": f"Comment {comment_id} deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting comment {comment_id}: {str(e)}")
            return {"status": "error", "message": str(e), "data": None}


# Global storage integration service instance
storage_integration_service = StorageIntegrationService()