import structlog
from typing import Dict, Any, List, Optional

from tempory.core import BaseScopedTools
from .services.storage_integration import storage_integration_service
from .services.storage_service import storage_service

logger = structlog.getLogger(__name__)


class StorageTools(BaseScopedTools):
    """MCP tools for File Storage operations - Complete implementation with all 33 tools"""

    def __init__(self, mcp_server):
        super().__init__(mcp_server, scope='storage')

    def _register_tools(self):
        """Register ALL MCP tools for file storage management"""
        logger.info("Registering Storage tools", scope=self.scope)

        # Connector discovery tools (2)
        self.register_tool(name="storage_list_connectors")(self.list_connectors)
        self.register_tool(name="storage_list_integrations")(self.list_integrations)

        # Drive tools (2)
        self.register_tool(name="storage_list_drives")(self.list_drives)
        self.register_tool(name="storage_get_drive_details")(self.get_drive_details)

        # Folder tools (5)
        self.register_tool(name="storage_list_folders")(self.list_folders)
        self.register_tool(name="storage_get_folder_details")(self.get_folder_details)
        self.register_tool(name="storage_create_folder")(self.create_folder)
        self.register_tool(name="storage_update_folder")(self.update_folder)
        self.register_tool(name="storage_delete_folder")(self.delete_folder)

        # File tools (5)
        self.register_tool(name="storage_list_files")(self.list_files)
        self.register_tool(name="storage_get_file_details")(self.get_file_details)
        self.register_tool(name="storage_create_file")(self.create_file)
        self.register_tool(name="storage_update_file")(self.update_file)
        self.register_tool(name="storage_delete_file")(self.delete_file)

        # User tools (2)
        self.register_tool(name="storage_list_users")(self.list_users)
        self.register_tool(name="storage_get_user_details")(self.get_user_details)

        # Group tools (2)
        self.register_tool(name="storage_list_groups")(self.list_groups)
        self.register_tool(name="storage_get_group_details")(self.get_group_details)

        # Version tools (2)
        self.register_tool(name="storage_list_versions")(self.list_versions)
        self.register_tool(name="storage_get_version_details")(self.get_version_details)

        # Permission tools (4)
        self.register_tool(name="storage_list_permissions")(self.list_permissions)
        self.register_tool(name="storage_get_permission_details")(self.get_permission_details)
        self.register_tool(name="storage_add_permission")(self.add_permission)
        self.register_tool(name="storage_delete_permission")(self.delete_permission)

        # Comment tools (5)
        self.register_tool(name="storage_list_comments")(self.list_comments)
        self.register_tool(name="storage_get_comment_details")(self.get_comment_details)
        self.register_tool(name="storage_create_comment")(self.create_comment)
        self.register_tool(name="storage_update_comment")(self.update_comment)
        self.register_tool(name="storage_delete_comment")(self.delete_comment)

        logger.info("Storage tools registration complete", total_tools=33)

    # ========== CONNECTOR TOOLS (2) ==========
    async def list_connectors(self) -> List[dict]:
        """
        Get list of available file storage connectors.

        Returns available storage service connectors (e.g., Google Drive, OneDrive, SharePoint, Box, Dropbox).
        """
        logger.info("MCP tool: list_connectors called for storage")
        connectors = await storage_integration_service.get_connectors()
        return [connector.dict() if hasattr(connector, 'dict') else connector for connector in connectors]

    async def list_integrations(self, connector: str) -> List[dict]:
        """
        Get integrations for a specific file storage connector.

        Args:
           connector: The storage connector name (e.g., 'google_drive', 'onedrive', 'sharepoint')

        Returns list of configured integrations for the specified storage connector.
        """
        logger.info(f"MCP tool: list_integrations called for Storage connector: {connector}")
        integrations = await storage_integration_service.get_integrations(connector)
        return [integration.dict() if hasattr(integration, 'dict') else integration for integration in integrations]

    # ========== DRIVE TOOLS (2) ==========
    async def list_drives(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List drives accessible through the integration.

        Args:
            integration_id: Unique identifier for the storage integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,-createdDateTime')

        Returns list of drives with metadata including name, ID, and URLs.
        """
        logger.info(f"MCP tool: list_drives called for integration: {integration_id}")
        return await storage_service.list_drives(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_drive_details(
            self,
            integration_id: str,
            drive_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific drive.

        Args:
            integration_id: Unique identifier for the storage integration
            drive_id: Unique identifier of the drive

        Returns detailed drive information including metadata and access URLs.
        """
        logger.info(f"MCP tool: get_drive_details called for drive: {drive_id}")
        return await storage_service.get_drive_details(
            integration_id=integration_id,
            drive_id=drive_id
        )

    # ========== FOLDER TOOLS (5) ==========
    async def list_folders(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List folders accessible through the integration.

        Args:
            integration_id: Unique identifier for the storage integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,-lastUpdatedDateTime,size')

        Returns list of folders with metadata including name, ID, size, and URLs.
        """
        logger.info(f"MCP tool: list_folders called for integration: {integration_id}")
        return await storage_service.list_folders(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_folder_details(
            self,
            integration_id: str,
            folder_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific folder.

        Args:
            integration_id: Unique identifier for the storage integration
            folder_id: Unique identifier of the folder

        Returns detailed folder information including metadata, size, and access URLs.
        """
        logger.info(f"MCP tool: get_folder_details called for folder: {folder_id}")
        return await storage_service.get_folder_details(
            integration_id=integration_id,
            folder_id=folder_id
        )

    async def create_folder(
            self,
            integration_id: str,
            name: str,
            description: Optional[str] = None,
            size: Optional[str] = None,
            folder_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new folder in the storage system.

        Args:
            integration_id: Unique identifier for the storage integration
            name: Name of the folder to create (required)
            description: Optional description of the folder
            size: Optional folder size
            folder_url: Optional folder URL

        Returns the created folder details including ID and metadata.
        """
        logger.info(f"MCP tool: create_folder called for integration: {integration_id}")
        return await storage_service.create_folder(
            integration_id=integration_id,
            name=name,
            description=description,
            size=size,
            folder_url=folder_url
        )

    async def update_folder(
            self,
            integration_id: str,
            folder_id: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            size: Optional[str] = None,
            folder_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing folder's metadata.

        Args:
            integration_id: Unique identifier for the storage integration
            folder_id: Unique identifier of the folder to update
            name: New name for the folder
            description: New description for the folder
            size: Updated folder size
            folder_url: Updated folder URL

        Returns the updated folder details.
        """
        logger.info(f"MCP tool: update_folder called for folder: {folder_id}")
        return await storage_service.update_folder(
            integration_id=integration_id,
            folder_id=folder_id,
            name=name,
            description=description,
            size=size,
            folder_url=folder_url
        )

    async def delete_folder(
            self,
            integration_id: str,
            folder_id: str
    ) -> Dict[str, Any]:
        """
        Delete a folder from the storage system.

        Args:
            integration_id: Unique identifier for the storage integration
            folder_id: Unique identifier of the folder to delete

        Returns confirmation of folder deletion.
        """
        logger.info(f"MCP tool: delete_folder called for folder: {folder_id}")
        return await storage_service.delete_folder(
            integration_id=integration_id,
            folder_id=folder_id
        )

    # ========== FILE TOOLS (5) ==========
    async def list_files(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List files accessible through the integration.

        Args:
            integration_id: Unique identifier for the storage integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,-lastUpdatedDateTime,size,mimeType')

        Returns list of files with metadata including name, ID, size, MIME type, and URLs.
        """
        logger.info(f"MCP tool: list_files called for integration: {integration_id}")
        return await storage_service.list_files(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_file_details(
            self,
            integration_id: str,
            file_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific file.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file

        Returns detailed file information including metadata, size, MIME type, and access URLs.
        """
        logger.info(f"MCP tool: get_file_details called for file: {file_id}")
        return await storage_service.get_file_details(
            integration_id=integration_id,
            file_id=file_id
        )

    async def create_file(
            self,
            integration_id: str,
            name: str,
            description: Optional[str] = None,
            size: Optional[str] = None,
            mime_type: Optional[str] = None,
            file_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new file in the storage system.

        Args:
            integration_id: Unique identifier for the storage integration
            name: Name of the file to create (required)
            description: Optional description of the file
            size: Optional file size
            mime_type: Optional MIME type (e.g., 'application/pdf', 'image/png')
            file_url: Optional file URL

        Returns the created file details including ID and metadata.
        """
        logger.info(f"MCP tool: create_file called for integration: {integration_id}")
        return await storage_service.create_file(
            integration_id=integration_id,
            name=name,
            description=description,
            size=size,
            mime_type=mime_type,
            file_url=file_url
        )

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
        """
        Update an existing file's metadata.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file to update
            name: New name for the file
            description: New description for the file
            size: Updated file size
            mime_type: Updated MIME type
            file_url: Updated file URL

        Returns the updated file details.
        """
        logger.info(f"MCP tool: update_file called for file: {file_id}")
        return await storage_service.update_file(
            integration_id=integration_id,
            file_id=file_id,
            name=name,
            description=description,
            size=size,
            mime_type=mime_type,
            file_url=file_url
        )

    async def delete_file(
            self,
            integration_id: str,
            file_id: str
    ) -> Dict[str, Any]:
        """
        Delete a file from the storage system.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file to delete

        Returns confirmation of file deletion.
        """
        logger.info(f"MCP tool: delete_file called for file: {file_id}")
        return await storage_service.delete_file(
            integration_id=integration_id,
            file_id=file_id
        )

    # ========== USER TOOLS (2) ==========
    async def list_users(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List users with access to the storage system.

        Args:
            integration_id: Unique identifier for the storage integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,-emailAddress,status')

        Returns list of users with metadata including name, email, status, and admin flag.
        """
        logger.info(f"MCP tool: list_users called for integration: {integration_id}")
        return await storage_service.list_users(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_user_details(
            self,
            integration_id: str,
            user_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific user.

        Args:
            integration_id: Unique identifier for the storage integration
            user_id: Unique identifier of the user

        Returns detailed user information including name, email, status, and admin privileges.
        """
        logger.info(f"MCP tool: get_user_details called for user: {user_id}")
        return await storage_service.get_user_details(
            integration_id=integration_id,
            user_id=user_id
        )

    # ========== GROUP TOOLS (2) ==========
    async def list_groups(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List groups in the storage system.

        Args:
            integration_id: Unique identifier for the storage integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,-membersCount,emailAddress')

        Returns list of groups with metadata including name, description, email, and member count.
        """
        logger.info(f"MCP tool: list_groups called for integration: {integration_id}")
        return await storage_service.list_groups(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_group_details(
            self,
            integration_id: str,
            group_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific group.

        Args:
            integration_id: Unique identifier for the storage integration
            group_id: Unique identifier of the group

        Returns detailed group information including name, description, members, and email.
        """
        logger.info(f"MCP tool: get_group_details called for group: {group_id}")
        return await storage_service.get_group_details(
            integration_id=integration_id,
            group_id=group_id
        )

    # ========== VERSION TOOLS (2) ==========
    async def list_versions(
            self,
            integration_id: str,
            file_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List file versions in the storage system.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,-createdDateTime')

        Returns list of file versions with metadata and version history.
        """
        logger.info(f"MCP tool: list_versions called for file: {file_id}")
        return await storage_service.list_versions(
            integration_id=integration_id,
            file_id=file_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_version_details(
            self,
            integration_id: str,
            file_id: str,
            version_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific file version.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file
            version_id: Unique identifier of the version

        Returns detailed version information including changes, timestamp, and author.
        """
        logger.info(f"MCP tool: get_version_details called for version: {version_id}")
        return await storage_service.get_version_details(
            integration_id=integration_id,
            file_id=file_id,
            version_id=version_id
        )

    # ========== PERMISSION TOOLS (4) ==========
    async def list_permissions(
            self,
            integration_id: str,
            file_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List permissions for a specific file.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'username,-createdDateTime')

        Returns list of permissions with user details and access levels.
        """
        logger.info(f"MCP tool: list_permissions called for file: {file_id}")
        return await storage_service.list_permissions(
            integration_id=integration_id,
            file_id=file_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_permission_details(
            self,
            integration_id: str,
            file_id: str,
            permission_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific permission.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file
            permission_id: Unique identifier of the permission

        Returns detailed permission information including user, access level, and scope.
        """
        logger.info(f"MCP tool: get_permission_details called for permission: {permission_id}")
        return await storage_service.get_permission_details(
            integration_id=integration_id,
            file_id=file_id,
            permission_id=permission_id
        )

    async def add_permission(
            self,
            integration_id: str,
            file_id: str,
            user_role: Optional[str] = None,
            user_type: Optional[str] = None,
            email_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new permission to a file.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file
            user_role: User role (e.g., 'reader', 'writer', 'owner')
            user_type: User type (e.g., 'user', 'group')
            email_address: Email address of the user/group

        Returns the created permission details.
        """
        logger.info(f"MCP tool: add_permission called for file: {file_id}")
        return await storage_service.add_permission(
            integration_id=integration_id,
            file_id=file_id,
            user_role=user_role,
            user_type=user_type,
            email_address=email_address
        )

    async def delete_permission(
            self,
            integration_id: str,
            file_id: str,
            permission_id: str
    ) -> Dict[str, Any]:
        """
        Delete a permission from a file.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file
            permission_id: Unique identifier of the permission to delete

        Returns confirmation of permission deletion.
        """
        logger.info(f"MCP tool: delete_permission called for permission: {permission_id}")
        return await storage_service.delete_permission(
            integration_id=integration_id,
            file_id=file_id,
            permission_id=permission_id
        )

    # ========== COMMENT TOOLS (5) ==========
    async def list_comments(
            self,
            integration_id: str,
            file_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List comments for a specific file.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'createdDateTime,-username')

        Returns list of comments with content, author, and timestamps.
        """
        logger.info(f"MCP tool: list_comments called for file: {file_id}")
        return await storage_service.list_comments(
            integration_id=integration_id,
            file_id=file_id,
            offset=offset,
            limit=limit,
            sort=sort
        )

    async def get_comment_details(
            self,
            integration_id: str,
            file_id: str,
            comment_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific comment.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file
            comment_id: Unique identifier of the comment

        Returns detailed comment information including content, author, and edit history.
        """
        logger.info(f"MCP tool: get_comment_details called for comment: {comment_id}")
        return await storage_service.get_comment_details(
            integration_id=integration_id,
            file_id=file_id,
            comment_id=comment_id
        )

    async def create_comment(
            self,
            integration_id: str,
            file_id: str,
            content: str,
            username: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new comment on a file.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file
            content: Comment content text (required)
            username: Optional username of the comment author

        Returns the created comment details including ID and metadata.
        """
        logger.info(f"MCP tool: create_comment called for file: {file_id}")
        return await storage_service.create_comment(
            integration_id=integration_id,
            file_id=file_id,
            content=content,
            username=username
        )

    async def update_comment(
            self,
            integration_id: str,
            file_id: str,
            comment_id: str,
            content: Optional[str] = None,
            username: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing comment.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file
            comment_id: Unique identifier of the comment to update
            content: New comment content text
            username: Updated username

        Returns the updated comment details.
        """
        logger.info(f"MCP tool: update_comment called for comment: {comment_id}")
        return await storage_service.update_comment(
            integration_id=integration_id,
            file_id=file_id,
            comment_id=comment_id,
            content=content,
            username=username
        )

    async def delete_comment(
            self,
            integration_id: str,
            file_id: str,
            comment_id: str
    ) -> Dict[str, Any]:
        """
        Delete a comment from a file.

        Args:
            integration_id: Unique identifier for the storage integration
            file_id: Unique identifier of the file
            comment_id: Unique identifier of the comment to delete

        Returns confirmation of comment deletion.
        """
        logger.info(f"MCP tool: delete_comment called for comment: {comment_id}")
        return await storage_service.delete_comment(
            integration_id=integration_id,
            file_id=file_id,
            comment_id=comment_id
        )