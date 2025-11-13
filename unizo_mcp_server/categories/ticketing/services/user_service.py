import structlog
import traceback
from typing import Dict, Any, Optional

from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request
from ..models.ticket_models import UserResponse

logger = structlog.getLogger(__name__)


class UserService:
    async def list_users(
            self,
            integration_id: str,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all users"""
        logger.info(f"Listing users for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            # Build query parameters
            params = {}
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if sort is not None:
                params["sort"] = sort

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/users"
            response = await http_client_service.make_request("get", url, headers, params=params)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                users_data = response.json().get("data", [])
                pagination = response.json().get("pagination")
            else:
                users_data = response.get("data", [])  # Already a dict
                pagination = response.get("pagination")

            users = [
                UserResponse(
                    id=user.get("id", "unknown"),
                    email=user.get("email"),
                    first_name=user.get("firstName"),
                    last_name=user.get("lastName"),
                    username=user.get("username"),
                    status=user.get("status"),
                    role=user.get("role"),
                    last_login=user.get("lastLogin"),
                    created_at=user.get("createdAt"),
                    updated_at=user.get("updatedAt")
                )
                for user in users_data
            ]

            result = {
                "status": "success",
                "message": f"Found {len(users)} users",
                "users": [user.dict() for user in users],
                "pagination": pagination
            }

            logger.info(f"Successfully retrieved {len(users)} users")
            return result
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_user(
            self,
            integration_id: str,
            user_id: str
    ) -> Dict[str, Any]:
        """Get user by identifier"""
        logger.info(f"Getting user: {user_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            # Note: The API spec shows this endpoint path, but it appears to be incorrect
            # It should be /api/v1/ticketing/users/{userId} instead of /api/v1/ticketing/organizations/{userId}
            # Using the corrected path here
            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/users/{user_id}"
            response = await http_client_service.make_request("get", url, headers)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                user_data = response.json()
            else:
                user_data = response  # Already a dict

            user = UserResponse(
                id=user_data.get("id", "unknown"),
                email=user_data.get("email"),
                first_name=user_data.get("firstName"),
                last_name=user_data.get("lastName"),
                username=user_data.get("username"),
                status=user_data.get("status"),
                role=user_data.get("role"),
                last_login=user_data.get("lastLogin"),
                created_at=user_data.get("createdAt"),
                updated_at=user_data.get("updatedAt")
            )

            result = {
                "status": "success",
                "message": "User retrieved successfully",
                "user": user.dict()
            }

            logger.info(f"User retrieved successfully: {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


user_service = UserService()