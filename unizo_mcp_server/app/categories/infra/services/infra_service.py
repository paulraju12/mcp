import traceback
import structlog
from typing import Dict, Any, Optional, List
from .infra_integration import infra_integration_service

logger = structlog.getLogger(__name__)


class InfraService:
    """Service for managing infrastructure operations"""

    # ========== ACCOUNT SERVICES ==========
    async def list_accounts(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List accounts with pagination"""
        logger.info(f"Listing accounts for integration: {integration_id}")
        try:
            result = await infra_integration_service.list_accounts(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                accounts_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(accounts_data)} accounts",
                    "data": {
                        "accounts": accounts_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(accounts_data)) if pagination else len(accounts_data)
                    }
                }
            else:
                return result
        except Exception as e:
            logger.error(f"Error in list_accounts: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_account_details(
            self,
            integration_id: str,
            account_id: str
    ) -> Dict[str, Any]:
        """Get account details"""
        logger.info(f"Getting account details for: {account_id}")
        try:
            result = await infra_integration_service.get_account(
                integration_id=integration_id,
                account_id=account_id
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Retrieved account {account_id}",
                    "data": {"account": result["data"]}
                }
            else:
                return result
        except Exception as e:
            logger.error(f"Error getting account details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # ========== COLLECTION SERVICES ==========
    async def list_collections(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List collections with pagination"""
        logger.info(f"Listing collections for integration: {integration_id}")
        try:
            result = await infra_integration_service.list_collections(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                collections_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(collections_data)} collections",
                    "data": {
                        "collections": collections_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(collections_data)) if pagination else len(collections_data)
                    }
                }
            else:
                return result
        except Exception as e:
            logger.error(f"Error in list_collections: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_collection_details(
            self,
            integration_id: str,
            collection_id: str
    ) -> Dict[str, Any]:
        """Get collection details"""
        logger.info(f"Getting collection details for: {collection_id}")
        try:
            result = await infra_integration_service.get_collection(
                integration_id=integration_id,
                collection_id=collection_id
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Retrieved collection {collection_id}",
                    "data": {"collection": result["data"]}
                }
            else:
                return result
        except Exception as e:
            logger.error(f"Error getting collection details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # ========== USER SERVICES ==========
    async def list_users(
            self,
            integration_id: str,
            collection_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List users in collection"""
        logger.info(f"Listing users for collection: {collection_id}")
        try:
            result = await infra_integration_service.list_users(
                integration_id=integration_id,
                collection_id=collection_id,
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
                        "collection_id": collection_id,
                        "total_count": pagination.get("total", len(users_data)) if pagination else len(users_data)
                    }
                }
            else:
                return result
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_user_details(
            self,
            integration_id: str,
            collection_id: str,
            user_id: str
    ) -> Dict[str, Any]:
        """Get user details"""
        logger.info(f"Getting user details for: {user_id}")
        try:
            result = await infra_integration_service.get_user(
                integration_id=integration_id,
                collection_id=collection_id,
                user_id=user_id
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Retrieved user {user_id}",
                    "data": {
                        "user": result["data"],
                        "collection_id": collection_id
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

    # ========== RESOURCE SERVICES ==========
    async def list_resources(
            self,
            integration_id: str,
            collection_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            parent_resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List resources in collection"""
        logger.info(f"Listing resources for collection: {collection_id}")
        try:
            result = await infra_integration_service.list_resources(
                integration_id=integration_id,
                collection_id=collection_id,
                offset=offset,
                limit=limit,
                sort=sort,
                parent_resource_id=parent_resource_id
            )

            if result["status"] == "success":
                resources_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(resources_data)} resources",
                    "data": {
                        "resources": resources_data,
                        "pagination": pagination,
                        "collection_id": collection_id,
                        "total_count": pagination.get("total", len(resources_data)) if pagination else len(resources_data)
                    }
                }
            else:
                return result
        except Exception as e:
            logger.error(f"Error listing resources: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_resource_details(
            self,
            integration_id: str,
            collection_id: str,
            resource_id: str,
            parent_resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get resource details"""
        logger.info(f"Getting resource details for: {resource_id}")
        try:
            result = await infra_integration_service.get_resource(
                integration_id=integration_id,
                collection_id=collection_id,
                resource_id=resource_id,
                parent_resource_id=parent_resource_id
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Retrieved resource {resource_id}",
                    "data": {
                        "resource": result["data"],
                        "collection_id": collection_id
                    }
                }
            else:
                return result
        except Exception as e:
            logger.error(f"Error getting resource details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # ========== POLICY SERVICES ==========
    async def list_policies(
            self,
            integration_id: str,
            collection_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List policies in collection"""
        logger.info(f"Listing policies for collection: {collection_id}")
        try:
            result = await infra_integration_service.list_policies(
                integration_id=integration_id,
                collection_id=collection_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                policies_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(policies_data)} policies",
                    "data": {
                        "policies": policies_data,
                        "pagination": pagination,
                        "collection_id": collection_id,
                        "total_count": pagination.get("total", len(policies_data)) if pagination else len(policies_data)
                    }
                }
            else:
                return result
        except Exception as e:
            logger.error(f"Error listing policies: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_policy_details(
            self,
            integration_id: str,
            collection_id: str,
            policy_id: str
    ) -> Dict[str, Any]:
        """Get policy details"""
        logger.info(f"Getting policy details for: {policy_id}")
        try:
            result = await infra_integration_service.get_policy(
                integration_id=integration_id,
                collection_id=collection_id,
                policy_id=policy_id
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Retrieved policy {policy_id}",
                    "data": {
                        "policy": result["data"],
                        "collection_id": collection_id
                    }
                }
            else:
                return result
        except Exception as e:
            logger.error(f"Error getting policy details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # ========== ROLE SERVICES ==========
    async def list_roles(
            self,
            integration_id: str,
            collection_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List roles in collection"""
        logger.info(f"Listing roles for collection: {collection_id}")
        try:
            result = await infra_integration_service.list_roles(
                integration_id=integration_id,
                collection_id=collection_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                roles_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(roles_data)} roles",
                    "data": {
                        "roles": roles_data,
                        "pagination": pagination,
                        "collection_id": collection_id,
                        "total_count": pagination.get("total", len(roles_data)) if pagination else len(roles_data)
                    }
                }
            else:
                return result
        except Exception as e:
            logger.error(f"Error listing roles: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_role_details(
            self,
            integration_id: str,
            collection_id: str,
            role_id: str
    ) -> Dict[str, Any]:
        """Get role details"""
        logger.info(f"Getting role details for: {role_id}")
        try:
            result = await infra_integration_service.get_role(
                integration_id=integration_id,
                collection_id=collection_id,
                role_id=role_id
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Retrieved role {role_id}",
                    "data": {
                        "role": result["data"],
                        "collection_id": collection_id
                    }
                }
            else:
                return result
        except Exception as e:
            logger.error(f"Error getting role details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


# Global infra service instance
infra_service = InfraService()