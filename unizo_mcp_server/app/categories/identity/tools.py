import structlog
from typing import Dict, Any, List, Optional

from .services.identity_integration import identity_integration_service
from .services.identity_service import identity_service
from tempory.core import BaseScopedTools

logger = structlog.getLogger(__name__)


class IdentityTools(BaseScopedTools):
    """MCP tools for Identity API operations"""

    def __init__(self, mcp_server):
        super().__init__(mcp_server, scope='identity')

    def _register_tools(self):
        """Register all MCP tools for identity management"""
        # Connector tools
        self.register_tool(name="identity_list_connectors")(self.list_connectors)
        self.register_tool(name="identity_list_integrations")(self.list_integrations)

        # User tools
        self.register_tool(name="identity_list_users")(self.list_users)
        self.register_tool(name="identity_get_user_details")(self.get_user_details)

        # Group tools
        self.register_tool(name="identity_list_groups")(self.list_groups)
        self.register_tool(name="identity_get_group_details")(self.get_group_details)

        # Group member tools
        self.register_tool(name="identity_list_group_members")(self.list_group_members)
        self.register_tool(name="identity_get_group_member_details")(self.get_group_member_details)

        # Session tools
        self.register_tool(name="identity_list_user_sessions")(self.list_user_sessions)
        self.register_tool(name="identity_get_session_details")(self.get_session_details)

        # Audit log tools
        self.register_tool(name="identity_list_audit_logs")(self.list_audit_logs)
        #self.register_tool(name="identity_get_audit_log_details")(self.get_audit_log_details)

    # ---------- CONNECTOR TOOLS ----------
    async def list_connectors(self) -> List[dict]:
        """Get list of available identity connectors"""
        logger.info("MCP tool: list_connectors called for identity")
        connectors = await identity_integration_service.get_connectors()
        return [connector.dict() if hasattr(connector, 'dict') else connector for connector in connectors]

    async def list_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific connector"""
        logger.info(f"MCP tool: list_integrations called for identity connector: {connector}")
        integrations = await identity_integration_service.get_integrations(connector)
        return [integration.dict() if hasattr(integration, 'dict') else integration for integration in integrations]

    # ---------- USER TOOLS ----------
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
        """
        List users with comprehensive filtering options.

        Args:
            integration_id: Unique identifier for the integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'lastName,firstName,-createdAt')
            status: Filter by account status (ACTIVE, INACTIVE, PENDING, SUSPENDED, TERMINATED)
            mfa_status: Filter by MFA status (Enabled, Disabled, Pending, Required)
            user_type: Filter by user type (User, Admin, Service, System, Guest)
            search: Search users by name, email, or username (min 3 chars)
            domain: Filter users by authentication domain
            has_devices: Filter users who have registered devices
            last_login_days: Filter users who logged in within specified days
        """
        logger.info(f"MCP tool: list_users called for integration: {integration_id}")
        return await identity_service.list_users(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort,
            status=status,
            mfa_status=mfa_status,
            user_type=user_type,
            search=search,
            domain=domain,
            has_devices=has_devices,
            last_login_days=last_login_days
        )

    async def get_user_details(
            self,
            integration_id: str,
            user_id: str,
            expand: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific user.

        Args:
            integration_id: Unique identifier for the integration
            user_id: Unique identifier of the user
            expand: List of resources to expand (groups, devices, manager, sessions, all)
        """
        logger.info(f"MCP tool: get_user_details called for user: {user_id}")
        return await identity_service.get_user_details(
            integration_id=integration_id,
            user_id=user_id,
            expand=expand
        )

    # ---------- GROUP TOOLS ----------
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
        """
        List groups with filtering options.

        Args:
            integration_id: Unique identifier for the integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'name,-createdAt')
            group_type: Filter by group type (Security, Distribution, Universal, Mail_Enabled, Role_Based)
            status: Filter by group status (ACTIVE, INACTIVE, PENDING, ARCHIVED)
            search: Search groups by name or description (min 3 chars)
            has_members: Filter groups with members
            parent_group_id: Filter by parent group
        """
        logger.info(f"MCP tool: list_groups called for integration: {integration_id}")
        return await identity_service.list_groups(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort,
            group_type=group_type,
            status=status,
            search=search,
            has_members=has_members,
            parent_group_id=parent_group_id
        )

    async def get_group_details(
            self,
            integration_id: str,
            group_id: str,
            expand: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific group.

        Args:
            integration_id: Unique identifier for the integration
            group_id: Unique identifier of the group
            expand: List of resources to expand (members, owners, parentGroups, childGroups, all)
        """
        logger.info(f"MCP tool: get_group_details called for group: {group_id}")
        return await identity_service.get_group_details(
            integration_id=integration_id,
            group_id=group_id,
            expand=expand
        )

    # ---------- GROUP MEMBER TOOLS ----------
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
        """
        List members of a specific group.

        Args:
            integration_id: Unique identifier for the integration
            group_id: Unique identifier of the group
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            member_type: Filter by member type (user, group, servicePrincipal)
            status: Filter by membership status (active, pending, suspended, expired)
            search: Search members by name or email
        """
        logger.info(f"MCP tool: list_group_members called for group: {group_id}")
        return await identity_service.list_group_members(
            integration_id=integration_id,
            group_id=group_id,
            offset=offset,
            limit=limit,
            member_type=member_type,
            status=status,
            search=search
        )

    async def get_group_member_details(
            self,
            integration_id: str,
            group_id: str,
            member_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific group member.

        Args:
            integration_id: Unique identifier for the integration
            group_id: Unique identifier of the group
            member_id: Unique identifier of the member
        """
        logger.info(f"MCP tool: get_group_member_details called for member: {member_id}")
        return await identity_service.get_group_member_details(
            integration_id=integration_id,
            group_id=group_id,
            member_id=member_id
        )

    # ---------- SESSION TOOLS ----------
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
        """
        List sessions for a specific user.

        Args:
            integration_id: Unique identifier for the integration
            user_id: Unique identifier of the user
            status: Filter sessions by status (active, expired, revoked, all) - default: active
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            from_date: Filter sessions created after this date (ISO format)
            to_date: Filter sessions created before this date (ISO format)
        """
        logger.info(f"MCP tool: list_user_sessions called for user: {user_id}")
        return await identity_service.list_user_sessions(
            integration_id=integration_id,
            user_id=user_id,
            status=status,
            offset=offset,
            limit=limit,
            from_date=from_date,
            to_date=to_date
        )

    async def get_session_details(
            self,
            integration_id: str,
            user_id: str,
            session_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific session.

        Args:
            integration_id: Unique identifier for the integration
            user_id: Unique identifier of the user
            session_id: Unique identifier of the session
        """
        logger.info(f"MCP tool: get_session_details called for session: {session_id}")
        return await identity_service.get_session_details(
            integration_id=integration_id,
            user_id=user_id,
            session_id=session_id
        )

    # ---------- AUDIT LOG TOOLS ----------
    async def list_audit_logs(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            since: Optional[str] = None,
            log_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List audit logs with filtering options.

        Args:
            integration_id: Unique identifier for the integration
            offset: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
            sort: Sort criteria (e.g., 'eventPublished,-eventType')
            since: Filter logs published since this timestamp (ISO format)
            log_type: Filter by event type
        """
        logger.info(f"MCP tool: list_audit_logs called for integration: {integration_id}")
        return await identity_service.list_audit_logs(
            integration_id=integration_id,
            offset=offset,
            limit=limit,
            sort=sort,
            since=since,
            log_type=log_type
        )

    async def get_audit_log_details(
            self,
            integration_id: str,
            audit_log_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific audit log.

        Args:
            integration_id: Unique identifier for the integration
            audit_log_id: Unique identifier of the audit log
        """
        logger.info(f"MCP tool: get_audit_log_details called for log: {audit_log_id}")
        return await identity_service.get_audit_log_details(
            integration_id=integration_id,
            audit_log_id=audit_log_id
        )