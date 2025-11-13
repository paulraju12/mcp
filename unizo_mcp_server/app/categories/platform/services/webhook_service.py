import traceback
from typing import Dict, Any, Optional, List
import structlog
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request
from tempory.core import settings
from pydantic import BaseModel, Field

logger = structlog.getLogger(__name__)

from unizo_mcp_server.app.categories.platform.services.connect_agent import ResponseFormatter


class WebhookRequest(BaseModel):
    """Webhook request model"""
    name: str = Field(..., description="Name of the webhook")
    description: Optional[str] = Field(None, description="Description of the webhook")
    url: str = Field(..., description="Webhook URL")
    events: Optional[List[str]] = Field(None, description="List of events to subscribe to")
    active: Optional[bool] = Field(True, description="Whether the webhook is active")
    secret: Optional[str] = Field(None, description="Secret for webhook signature verification")
    ssl_verification: Optional[bool] = Field(True, description="Whether to verify SSL certificates")
    content_type: Optional[str] = Field("application/json", description="Content type for webhook payloads")


class WebhookActionRequest(BaseModel):
    """Webhook action request model"""
    action: str = Field(..., description="Action to perform (e.g., 'test', 'ping', 'redeliver')")
    delivery_id: Optional[str] = Field(None, description="Delivery ID for redelivery actions")


class WebhookService:
    @staticmethod
    async def list_webhooks(
            correlation_id: Optional[str] = None,
            offset: Optional[int] = 0,
            limit: Optional[int] = 100,
            sort: Optional[str] = None,
            webhook_event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all webhooks"""
        logger.info("Listing all webhooks")

        try:
            headers = extract_headers_from_request()
            if correlation_id:
                headers["correlationId"] = correlation_id

            url = f"{settings.integration_mgr_base_url}/api/v1/webhooks"

            params = {}
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if sort:
                params["sort"] = sort
            if webhook_event_type:
                params["webhookEventType"] = webhook_event_type

            response = await http_client_service.make_request("get", url, headers, params=params)

            # Handle different response formats
            if isinstance(response, dict):
                webhooks = response.get("data", response)
            elif isinstance(response, list):
                webhooks = response
            else:
                logger.warning(f"Unexpected response type: {type(response)}")
                webhooks = []

            return ResponseFormatter.success_response(
                message=f"Retrieved {len(webhooks)} webhooks",
                data={"webhooks": webhooks, "count": len(webhooks)}
            )

        except Exception as e:
            logger.error(f"Error listing webhooks: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to list webhooks: {str(e)}",
                error_details=traceback.format_exc()
            )

    @staticmethod
    async def get_webhook(
            webhook_id: str,
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get webhook by identifier"""
        logger.info(f"Getting webhook: {webhook_id}")

        try:
            headers = extract_headers_from_request()
            if correlation_id:
                headers["correlationId"] = correlation_id

            url = f"{settings.integration_mgr_base_url}/api/v1/webhooks/{webhook_id}"

            response = await http_client_service.make_request("get", url, headers)

            # Handle different response formats
            if isinstance(response, dict):
                webhook_data = response
            else:
                logger.warning(f"Unexpected response type: {type(response)}")
                webhook_data = {}

            return ResponseFormatter.success_response(
                message=f"Retrieved webhook {webhook_id}",
                data={"webhook": webhook_data}
            )

        except Exception as e:
            logger.error(f"Error getting webhook {webhook_id}: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to get webhook {webhook_id}: {str(e)}",
                error_details=traceback.format_exc()
            )

    @staticmethod
    async def create_webhook(
            webhook_request: WebhookRequest,
            correlation_id: Optional[str] = None,
            request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new webhook"""
        logger.info(f"Creating webhook: {webhook_request.name}")

        try:
            headers = extract_headers_from_request()
            if correlation_id:
                headers["correlationId"] = correlation_id
            if request_id:
                headers["requestid"] = request_id

            webhook_data = webhook_request.dict(exclude_none=True)
            url = f"{settings.integration_mgr_base_url}/api/v1/webhooks"

            response = await http_client_service.make_request("post", url, headers, json_data=webhook_data)

            # Handle different response formats
            if isinstance(response, dict):
                created_webhook = response
            else:
                logger.warning(f"Unexpected response type: {type(response)}")
                created_webhook = {}

            return ResponseFormatter.success_response(
                message=f"Webhook '{webhook_request.name}' created successfully",
                data={"webhook": created_webhook}
            )

        except Exception as e:
            logger.error(f"Error creating webhook {webhook_request.name}: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to create webhook {webhook_request.name}: {str(e)}",
                error_details=traceback.format_exc()
            )

    @staticmethod
    async def update_webhook(
            webhook_id: str,
            update_operations: List[Dict[str, Any]],
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update webhook by ID using PATCH operations"""
        logger.info(f"Updating webhook: {webhook_id}")

        try:
            headers = extract_headers_from_request()
            if correlation_id:
                headers["correlationId"] = correlation_id

            url = f"{settings.integration_mgr_base_url}/api/v1/webhooks/{webhook_id}"

            response = await http_client_service.make_request("patch", url, headers, json_data=update_operations)

            # Handle different response formats
            if isinstance(response, dict):
                updated_webhook = response
            else:
                logger.warning(f"Unexpected response type: {type(response)}")
                updated_webhook = {}

            return ResponseFormatter.success_response(
                message=f"Webhook {webhook_id} updated successfully",
                data={"webhook": updated_webhook}
            )

        except Exception as e:
            logger.error(f"Error updating webhook {webhook_id}: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to update webhook {webhook_id}: {str(e)}",
                error_details=traceback.format_exc()
            )

    @staticmethod
    async def delete_webhook(
            webhook_id: str,
            correlation_id: Optional[str] = None,
            request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delete webhook by identifier"""
        logger.info(f"Deleting webhook: {webhook_id}")

        try:
            headers = extract_headers_from_request()
            if correlation_id:
                headers["correlationId"] = correlation_id
            if request_id:
                headers["requestid"] = request_id

            url = f"{settings.integration_mgr_base_url}/api/v1/webhooks/{webhook_id}"

            response = await http_client_service.make_request("delete", url, headers)

            # Handle different response formats
            if isinstance(response, dict):
                deleted_webhook = response
            else:
                logger.warning(f"Unexpected response type: {type(response)}")
                deleted_webhook = {}

            return ResponseFormatter.success_response(
                message=f"Webhook {webhook_id} deleted successfully",
                data={"webhook": deleted_webhook}
            )

        except Exception as e:
            logger.error(f"Error deleting webhook {webhook_id}: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to delete webhook {webhook_id}: {str(e)}",
                error_details=traceback.format_exc()
            )

    @staticmethod
    async def create_webhook_action(
            webhook_id: str,
            action_request: WebhookActionRequest
    ) -> Dict[str, Any]:
        """Create webhook action"""
        logger.info(f"Creating action '{action_request.action}' for webhook: {webhook_id}")

        try:
            headers = extract_headers_from_request()

            action_data = action_request.dict(exclude_none=True)
            url = f"{settings.integration_mgr_base_url}/api/v1/webhooks/{webhook_id}/actions"

            response = await http_client_service.make_request("post", url, headers, json_data=action_data)

            # Handle different response formats
            if isinstance(response, dict):
                action_response = response
            else:
                logger.warning(f"Unexpected response type: {type(response)}")
                action_response = {}

            return ResponseFormatter.success_response(
                message=f"Action '{action_request.action}' executed successfully on webhook {webhook_id}",
                data={"action_result": action_response}
            )

        except Exception as e:
            logger.error(f"Error executing action '{action_request.action}' on webhook {webhook_id}: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to execute action '{action_request.action}' on webhook {webhook_id}: {str(e)}",
                error_details=traceback.format_exc()
            )