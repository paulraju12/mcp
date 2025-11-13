import traceback
import structlog
from typing import Dict, Any, Optional, List

from .identity_integration import identity_integration_service

logger = structlog.getLogger(__name__)


class IdentityService:
    """Service for managing identity operations"""

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
        """List users with comprehensive filtering options"""
        logger.info(f"Listing users for integration: {integration_id}")
        try:
            result = await identity_integration_service.list_users(
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
            user_id: str,
            expand: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get detailed information about a specific user"""
        logger.info(f"Getting user details for user: {user_id}")
        try:
            result = await identity_integration_service.get_user(
                integration_id=integration_id,
                user_id=user_id,
                expand=expand
            )

            if result["status"] == "success":
                user_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved user details for {user_id}",
                    "data": {
                        "user": user_data,
                        "expanded": expand or []
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
        """List groups with filtering options"""
        logger.info(f"Listing groups for integration: {integration_id}")
        try:
            result = await identity_integration_service.list_groups(
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
            group_id: str,
            expand: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get detailed information about a specific group"""
        logger.info(f"Getting group details for group: {group_id}")
        try:
            result = await identity_integration_service.get_group(
                integration_id=integration_id,
                group_id=group_id,
                expand=expand
            )

            if result["status"] == "success":
                group_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved group details for {group_id}",
                    "data": {
                        "group": group_data,
                        "expanded": expand or []
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
        logger.info(f"Listing members for group: {group_id}")
        try:
            result = await identity_integration_service.list_group_members(
                integration_id=integration_id,
                group_id=group_id,
                offset=offset,
                limit=limit,
                member_type=member_type,
                status=status,
                search=search
            )

            if result["status"] == "success":
                members_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(members_data)} members for group {group_id}",
                    "data": {
                        "members": members_data,
                        "pagination": pagination,
                        "group_id": group_id,
                        "total_count": pagination.get("total", len(members_data)) if pagination else len(members_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error listing group members: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_group_member_details(
            self,
            integration_id: str,
            group_id: str,
            member_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific group member"""
        logger.info(f"Getting member details for member: {member_id} in group: {group_id}")
        try:
            result = await identity_integration_service.get_group_member(
                integration_id=integration_id,
                group_id=group_id,
                member_id=member_id
            )

            if result["status"] == "success":
                member_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved member details for {member_id}",
                    "data": {
                        "member": member_data,
                        "group_id": group_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting group member details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
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
        logger.info(f"Listing sessions for user: {user_id}")
        try:
            result = await identity_integration_service.list_user_sessions(
                integration_id=integration_id,
                user_id=user_id,
                status=status,
                offset=offset,
                limit=limit,
                from_date=from_date,
                to_date=to_date
            )

            if result["status"] == "success":
                sessions_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(sessions_data)} sessions for user {user_id}",
                    "data": {
                        "sessions": sessions_data,
                        "pagination": pagination,
                        "user_id": user_id,
                        "total_count": pagination.get("total", len(sessions_data)) if pagination else len(sessions_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error listing user sessions: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_session_details(
            self,
            integration_id: str,
            user_id: str,
            session_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific session"""
        logger.info(f"Getting session details for session: {session_id}")
        try:
            result = await identity_integration_service.get_user_session(
                integration_id=integration_id,
                user_id=user_id,
                session_id=session_id
            )

            if result["status"] == "success":
                session_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved session details for {session_id}",
                    "data": {
                        "session": session_data,
                        "user_id": user_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting session details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
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
        """List audit logs with filtering options"""
        logger.info(f"Listing audit logs for integration: {integration_id}")
        try:
            result = await identity_integration_service.list_audit_logs(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort,
                since=since,
                log_type=log_type
            )

            if result["status"] == "success":
                logs_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(logs_data)} audit logs",
                    "data": {
                        "logs": logs_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(logs_data)) if pagination else len(logs_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_audit_logs: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_audit_log_details(
            self,
            integration_id: str,
            audit_log_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific audit log"""
        logger.info(f"Getting audit log details for log: {audit_log_id}")
        try:
            result = await identity_integration_service.get_audit_log(
                integration_id=integration_id,
                audit_log_id=audit_log_id
            )

            if result["status"] == "success":
                log_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved audit log details for {audit_log_id}",
                    "data": {
                        "log": log_data
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting audit log details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


# Global identity service instance
identity_service = IdentityService()