import traceback
from typing import Dict, Any, Optional, List
import structlog
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request
from tempory.core import settings
from ..models.platform import WatchRequest

logger = structlog.getLogger(__name__)

from unizo_mcp_server.app.categories.platform.services.connect_agent import ResponseFormatter


class WatchService:
    @staticmethod
    async def list_watches(
            integration_id: str,
            correlation_id: Optional[str] = None,
            offset: Optional[int] = 0,
            limit: Optional[int] = 100,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        logger.info(f"Listing watches for integration: {integration_id}")

        try:
            headers = extract_headers_from_request()
            if correlation_id:
                headers["correlationId"] = correlation_id

            url = f"{settings.integration_mgr_base_url}/api/v1/integrations/{integration_id}/watches"

            params = {}
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if sort:
                params["sort"] = sort

            response = await http_client_service.make_request("get", url, headers, params=params)

            # Handle different response formats
            if isinstance(response, dict):
                watches = response.get("data", response)
            elif isinstance(response, list):
                watches = response
            else:
                logger.warning(f"Unexpected response type: {type(response)}")
                watches = []

            return ResponseFormatter.success_response(
                message=f"Retrieved {len(watches)} watches for integration {integration_id}",
                data={"watches": watches, "count": len(watches)}
            )

        except Exception as e:
            logger.error(f"Error listing watches for integration {integration_id}: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to list watches for integration {integration_id}: {str(e)}",
                error_details=traceback.format_exc()
            )

    @staticmethod
    async def get_watch(
            integration_id: str,
            watch_id: str,
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        logger.info(f"Getting watch: {watch_id} for integration: {integration_id}")

        try:
            headers = extract_headers_from_request()
            if correlation_id:
                headers["correlationId"] = correlation_id

            url = f"{settings.integration_mgr_base_url}/api/v1/integrations/{integration_id}/watches/{watch_id}"

            response = await http_client_service.make_request("get", url, headers)

            # Handle different response formats
            if isinstance(response, dict):
                watch_data = response
            else:
                logger.warning(f"Unexpected response type: {type(response)}")
                watch_data = {}

            return ResponseFormatter.success_response(
                message=f"Retrieved watch {watch_id}",
                data={"watch": watch_data}
            )

        except Exception as e:
            logger.error(f"Error getting watch {watch_id}: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to get watch {watch_id}: {str(e)}",
                error_details=traceback.format_exc()
            )

    @staticmethod
    async def get_watch_internal(
            watch_id: str,
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get watch by identifier using internal API endpoint"""
        logger.info(f"Getting watch internally: {watch_id}")

        try:
            headers = extract_headers_from_request()
            if correlation_id:
                headers["correlationId"] = correlation_id

            url = f"{settings.integration_mgr_base_url}/api/i1/watches/{watch_id}"

            response = await http_client_service.make_request("get", url, headers)

            # Handle different response formats
            if isinstance(response, dict):
                watch_data = response
            else:
                logger.warning(f"Unexpected response type: {type(response)}")
                watch_data = {}

            return ResponseFormatter.success_response(
                message=f"Retrieved watch {watch_id} via internal API",
                data={"watch": watch_data}
            )

        except Exception as e:
            logger.error(f"Error getting watch {watch_id} via internal API: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to get watch {watch_id} via internal API: {str(e)}",
                error_details=traceback.format_exc()
            )

    @staticmethod
    async def create_watch(
            watch_request: WatchRequest,
            integration_id: str,
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        logger.info(f"Creating watch: {watch_request.name} for integration: {integration_id}")

        try:
            headers = extract_headers_from_request()
            if correlation_id:
                headers["correlationId"] = correlation_id

            watch_data = watch_request.dict(exclude_none=True)
            url = f"{settings.integration_mgr_base_url}/api/v1/integrations/{integration_id}/watches"

            response = await http_client_service.make_request("post", url, headers, json_data=watch_data)

            # Handle different response formats
            if isinstance(response, dict):
                created_watch = response
            else:
                logger.warning(f"Unexpected response type: {type(response)}")
                created_watch = {}

            return ResponseFormatter.success_response(
                message=f"Watch '{watch_request.name}' created successfully",
                data={"watch": created_watch}
            )

        except Exception as e:
            logger.error(f"Error creating watch {watch_request.name}: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to create watch {watch_request.name}: {str(e)}",
                error_details=traceback.format_exc()
            )

    @staticmethod
    async def update_watch(
            integration_id: str,
            watch_id: str,
            update_operations: List[Dict[str, Any]],
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update watch by ID using PATCH operations"""
        logger.info(f"Updating watch: {watch_id} for integration: {integration_id}")

        try:
            headers = extract_headers_from_request()
            if correlation_id:
                headers["correlationId"] = correlation_id

            url = f"{settings.integration_mgr_base_url}/api/v1/integrations/{integration_id}/watches/{watch_id}"

            response = await http_client_service.make_request("patch", url, headers, json_data=update_operations)

            # Handle different response formats
            if isinstance(response, dict):
                updated_watch = response
            else:
                logger.warning(f"Unexpected response type: {type(response)}")
                updated_watch = {}

            return ResponseFormatter.success_response(
                message=f"Watch {watch_id} updated successfully",
                data={"watch": updated_watch}
            )

        except Exception as e:
            logger.error(f"Error updating watch {watch_id}: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to update watch {watch_id}: {str(e)}",
                error_details=traceback.format_exc()
            )

    @staticmethod
    async def delete_watch(
            integration_id: str,
            watch_id: str,
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        logger.info(f"Deleting watch: {watch_id} for integration: {integration_id}")

        try:
            headers = extract_headers_from_request()
            if correlation_id:
                headers["correlationId"] = correlation_id

            url = f"{settings.integration_mgr_base_url}/api/v1/integrations/{integration_id}/watches/{watch_id}"

            response = await http_client_service.make_request("delete", url, headers)

            # Handle different response formats
            if isinstance(response, dict):
                deleted_watch = response
            else:
                logger.warning(f"Unexpected response type: {type(response)}")
                deleted_watch = {}

            return ResponseFormatter.success_response(
                message=f"Watch {watch_id} deleted successfully",
                data={"watch": deleted_watch}
            )

        except Exception as e:
            logger.error(f"Error deleting watch {watch_id}: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to delete watch {watch_id}: {str(e)}",
                error_details=traceback.format_exc()
            )