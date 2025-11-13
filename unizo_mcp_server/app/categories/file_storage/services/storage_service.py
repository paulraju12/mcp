import traceback
import structlog
from typing import Dict, Any, Optional

from .storage_integration import storage_integration_service

logger = structlog.getLogger(__name__)


class StorageService:
    """Service for managing File Storage operations"""

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
            result = await storage_integration_service.list_drives(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                drives_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(drives_data)} drives",
                    "data": {
                        "drives": drives_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(drives_data)) if pagination else len(drives_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_drives: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_drive_details(
            self,
            integration_id: str,
            drive_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific drive"""
        logger.info(f"Getting drive details for drive: {drive_id}")
        try:
            result = await storage_integration_service.get_drive(
                integration_id=integration_id,
                drive_id=drive_id
            )

            if result["status"] == "success":
                drive_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved drive details for {drive_id}",
                    "data": {
                        "drive": drive_data,
                        "drive_id": drive_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting drive details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

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
            result = await storage_integration_service.list_folders(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                folders_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(folders_data)} folders",
                    "data": {
                        "folders": folders_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(folders_data)) if pagination else len(folders_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_folders: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_folder_details(
            self,
            integration_id: str,
            folder_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific folder"""
        logger.info(f"Getting folder details for folder: {folder_id}")
        try:
            result = await storage_integration_service.get_folder(
                integration_id=integration_id,
                folder_id=folder_id
            )

            if result["status"] == "success":
                folder_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved folder details for {folder_id}",
                    "data": {
                        "folder": folder_data,
                        "folder_id": folder_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting folder details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_folder(
            self,
            integration_id: str,
            name: str,
            description: Optional[str] = None,
            size: Optional[str] = None,
            folder_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new folder"""
        logger.info(f"Creating folder for integration: {integration_id}")
        try:
            folder_data = {
                "name": name,
                "description": description,
                "size": size,
                "folderUrl": folder_url
            }
            folder_data = {k: v for k, v in folder_data.items() if v is not None}

            result = await storage_integration_service.create_folder(
                integration_id=integration_id,
                folder_data=folder_data
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": "Folder created successfully",
                    "data": result["data"]
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def update_folder(
            self,
            integration_id: str,
            folder_id: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            size: Optional[str] = None,
            folder_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing folder"""
        logger.info(f"Updating folder {folder_id} for integration: {integration_id}")
        try:
            folder_data = {
                "name": name,
                "description": description,
                "size": size,
                "folderUrl": folder_url
            }
            folder_data = {k: v for k, v in folder_data.items() if v is not None}

            result = await storage_integration_service.update_folder(
                integration_id=integration_id,
                folder_id=folder_id,
                folder_data=folder_data
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Folder {folder_id} updated successfully",
                    "data": result["data"]
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error updating folder: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def delete_folder(
            self,
            integration_id: str,
            folder_id: str
    ) -> Dict[str, Any]:
        """Delete a folder"""
        logger.info(f"Deleting folder {folder_id} for integration: {integration_id}")
        try:
            result = await storage_integration_service.delete_folder(
                integration_id=integration_id,
                folder_id=folder_id
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Folder {folder_id} deleted successfully",
                    "data": result["data"]
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error deleting folder: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

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
            result = await storage_integration_service.list_files(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                files_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(files_data)} files",
                    "data": {
                        "files": files_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(files_data)) if pagination else len(files_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_files: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_file_details(
            self,
            integration_id: str,
            file_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific file"""
        logger.info(f"Getting file details for file: {file_id}")
        try:
            result = await storage_integration_service.get_file(
                integration_id=integration_id,
                file_id=file_id
            )

            if result["status"] == "success":
                file_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved file details for {file_id}",
                    "data": {
                        "file": file_data,
                        "file_id": file_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting file details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_file(
            self,
            integration_id: str,
            name: str,
            description: Optional[str] = None,
            size: Optional[str] = None,
            mime_type: Optional[str] = None,
            file_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new file"""
        logger.info(f"Creating file for integration: {integration_id}")
        try:
            file_data = {
                "name": name,
                "description": description,
                "size": size,
                "mimeType": mime_type,
                "fileUrl": file_url
            }
            file_data = {k: v for k, v in file_data.items() if v is not None}

            result = await storage_integration_service.create_file(
                integration_id=integration_id,
                file_data=file_data
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": "File created successfully",
                    "data": result["data"]
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error creating file: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def update_file(
            self,
            integration_id: str,
            file_id: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            size: Optional[str] = None,
            mime_type: Optional[str] = None,
            file_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing file"""
        logger.info(f"Updating file {file_id} for integration: {integration_id}")
        try:
            file_data = {
                "name": name,
                "description": description,
                "size": size,
                "mimeType": mime_type,
                "fileUrl": file_url
            }
            file_data = {k: v for k, v in file_data.items() if v is not None}

            result = await storage_integration_service.update_file(
                integration_id=integration_id,
                file_id=file_id,
                file_data=file_data
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"File {file_id} updated successfully",
                    "data": result["data"]
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error updating file: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def delete_file(
            self,
            integration_id: str,
            file_id: str
    ) -> Dict[str, Any]:
        """Delete a file"""
        logger.info(f"Deleting file {file_id} for integration: {integration_id}")
        try:
            result = await storage_integration_service.delete_file(
                integration_id=integration_id,
                file_id=file_id
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"File {file_id} deleted successfully",
                    "data": result["data"]
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

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
            result = await storage_integration_service.list_users(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                users_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(users_data)} users",
                    "data": {
                        "users": users_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(users_data)) if pagination else len(users_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_users: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_user_details(
            self,
            integration_id: str,
            user_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific user"""
        logger.info(f"Getting user details for user: {user_id}")
        try:
            result = await storage_integration_service.get_user(
                integration_id=integration_id,
                user_id=user_id
            )

            if result["status"] == "success":
                user_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved user details for {user_id}",
                    "data": {
                        "user": user_data,
                        "user_id": user_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting user details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

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
            result = await storage_integration_service.list_groups(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                groups_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(groups_data)} groups",
                    "data": {
                        "groups": groups_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(groups_data)) if pagination else len(groups_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_groups: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_group_details(
            self,
            integration_id: str,
            group_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific group"""
        logger.info(f"Getting group details for group: {group_id}")
        try:
            result = await storage_integration_service.get_group(
                integration_id=integration_id,
                group_id=group_id
            )

            if result["status"] == "success":
                group_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved group details for {group_id}",
                    "data": {
                        "group": group_data,
                        "group_id": group_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting group details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()

            }

# ---------- VERSION OPERATIONS ----------
    async def list_versions(
            self,
            integration_id: str,
            file_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List versions for a specific file"""
        logger.info(f"Listing versions for file {file_id}")
        try:
            result = await storage_integration_service.list_versions(
                integration_id=integration_id,
                file_id=file_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                versions_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(versions_data)} versions for file {file_id}",
                    "data": {
                        "versions": versions_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(versions_data)) if pagination else len(versions_data),
                        "file_id": file_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_versions: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_version_details(
            self,
            integration_id: str,
            file_id: str,
            version_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific version"""
        logger.info(f"Getting version details for version: {version_id}")
        try:
            result = await storage_integration_service.get_version(
                integration_id=integration_id,
                file_id=file_id,
                version_id=version_id
            )

            if result["status"] == "success":
                version_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved version details for {version_id}",
                    "data": {
                        "version": version_data,
                        "version_id": version_id,
                        "file_id": file_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting version details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # ---------- PERMISSION OPERATIONS ----------
    async def list_permissions(
            self,
            integration_id: str,
            file_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List permissions for a specific file"""
        logger.info(f"Listing permissions for file {file_id}")
        try:
            result = await storage_integration_service.list_permissions(
                integration_id=integration_id,
                file_id=file_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                permissions_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(permissions_data)} permissions for file {file_id}",
                    "data": {
                        "permissions": permissions_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(permissions_data)) if pagination else len(permissions_data),
                        "file_id": file_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_permissions: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_permission_details(
            self,
            integration_id: str,
            file_id: str,
            permission_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific permission"""
        logger.info(f"Getting permission details for permission: {permission_id}")
        try:
            result = await storage_integration_service.get_permission(
                integration_id=integration_id,
                file_id=file_id,
                permission_id=permission_id
            )

            if result["status"] == "success":
                permission_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved permission details for {permission_id}",
                    "data": {
                        "permission": permission_data,
                        "permission_id": permission_id,
                        "file_id": file_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting permission details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def add_permission(
            self,
            integration_id: str,
            file_id: str,
            user_role: Optional[str] = None,
            user_type: Optional[str] = None,
            email_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a new permission to a file"""
        logger.info(f"Adding permission for file {file_id}")
        try:
            permission_data = {
                "userRole": user_role,
                "userType": user_type,
                "emailAddress": email_address
            }
            permission_data = {k: v for k, v in permission_data.items() if v is not None}

            result = await storage_integration_service.add_permission(
                integration_id=integration_id,
                file_id=file_id,
                permission_data=permission_data
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Permission added successfully to file {file_id}",
                    "data": result["data"]
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error adding permission: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def delete_permission(
            self,
            integration_id: str,
            file_id: str,
            permission_id: str
    ) -> Dict[str, Any]:
        """Delete a permission from a file"""
        logger.info(f"Deleting permission {permission_id} for file {file_id}")
        try:
            result = await storage_integration_service.delete_permission(
                integration_id=integration_id,
                file_id=file_id,
                permission_id=permission_id
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Permission {permission_id} deleted successfully from file {file_id}",
                    "data": result["data"]
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error deleting permission: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # ---------- COMMENT OPERATIONS ----------
    async def list_comments(
            self,
            integration_id: str,
            file_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List comments for a specific file"""
        logger.info(f"Listing comments for file {file_id}")
        try:
            result = await storage_integration_service.list_comments(
                integration_id=integration_id,
                file_id=file_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                comments_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(comments_data)} comments for file {file_id}",
                    "data": {
                        "comments": comments_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(comments_data)) if pagination else len(comments_data),
                        "file_id": file_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_comments: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_comment_details(
            self,
            integration_id: str,
            file_id: str,
            comment_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific comment"""
        logger.info(f"Getting comment details for comment: {comment_id}")
        try:
            result = await storage_integration_service.get_comment(
                integration_id=integration_id,
                file_id=file_id,
                comment_id=comment_id
            )

            if result["status"] == "success":
                comment_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved comment details for {comment_id}",
                    "data": {
                        "comment": comment_data,
                        "comment_id": comment_id,
                        "file_id": file_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting comment details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_comment(
            self,
            integration_id: str,
            file_id: str,
            content: str,
            username: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new comment on a file"""
        logger.info(f"Creating comment for file {file_id}")
        try:
            comment_data = {
                "content": content,
                "username": username
            }
            comment_data = {k: v for k, v in comment_data.items() if v is not None}

            result = await storage_integration_service.create_comment(
                integration_id=integration_id,
                file_id=file_id,
                comment_data=comment_data
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Comment created successfully on file {file_id}",
                    "data": result["data"]
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def update_comment(
            self,
            integration_id: str,
            file_id: str,
            comment_id: str,
            content: Optional[str] = None,
            username: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing comment"""
        logger.info(f"Updating comment {comment_id} for file {file_id}")
        try:
            comment_data = {
                "content": content,
                "username": username
            }
            comment_data = {k: v for k, v in comment_data.items() if v is not None}

            result = await storage_integration_service.update_comment(
                integration_id=integration_id,
                file_id=file_id,
                comment_id=comment_id,
                comment_data=comment_data
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Comment {comment_id} updated successfully",
                    "data": result["data"]
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error updating comment: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def delete_comment(
            self,
            integration_id: str,
            file_id: str,
            comment_id: str
    ) -> Dict[str, Any]:
        """Delete a comment from a file"""
        logger.info(f"Deleting comment {comment_id} for file {file_id}")
        try:
            result = await storage_integration_service.delete_comment(
                integration_id=integration_id,
                file_id=file_id,
                comment_id=comment_id
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Comment {comment_id} deleted successfully from file {file_id}",
                    "data": result["data"]
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error deleting comment: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


# Global storage service instance
storage_service = StorageService()