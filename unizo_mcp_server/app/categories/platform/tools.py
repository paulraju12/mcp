import traceback
from typing import Optional, Any, Dict, List
import structlog

from .models.platform import WatchRequest, WatchType, WatchConfig, ResourceType, WatchResource, WebhookRequest, \
    WebhookActionRequest
from .services.connect_agent import ConnectService, StatusService, ResponseFormatter, PlatformListingService
from .services.watch import WatchService
from .services.webhook_service import WebhookService
from tempory.core import extract_headers_from_request
from tempory.core import BaseScopedTools

logger = structlog.getLogger(__name__)


class PlatformTools(BaseScopedTools):
    def __init__(self, mcp_server):
        super().__init__(mcp_server, scope="Platform")

    def _register_tools(self):
        """Register all MCP tools for platform"""
        # Connection and integration tools
        self.register_tool(name="connect_agent")(self.connect_agent)
        self.register_tool(name="status_check")(self.status_check)

        # Platform-wide listing tools
        #self.register_tool(name="list_all_available_connectors")(self.list_all_available_connectors)
        self.register_tool(name="list_all_available_integrations")(self.list_all_available_integrations)

        # Watch management tools
        self.register_tool(name="list_watches")(self.list_watches)
        self.register_tool(name="get_watch")(self.get_watch)
        self.register_tool(name="get_watch_internal")(self.get_watch_internal)
        self.register_tool(name="create_watch")(self.create_watch)
        self.register_tool(name="update_watch")(self.update_watch)
        self.register_tool(name="delete_watch")(self.delete_watch)

        # Webhook management tools
        self.register_tool(name="list_webhooks")(self.list_webhooks)
        self.register_tool(name="get_webhook")(self.get_webhook)
        self.register_tool(name="create_webhook")(self.create_webhook)
        self.register_tool(name="update_webhook")(self.update_webhook)
        self.register_tool(name="delete_webhook")(self.delete_webhook)
        self.register_tool(name="create_webhook_action")(self.create_webhook_action)

    async def connect_agent(
            self,
            step: str,
            connector_name: Optional[str] = None,
            connector_id: Optional[str] = None,
            connector_category: Optional[str] = None,
            integration_name: Optional[str] = None,
            auth_data: Optional[Dict[str, Any]] = None,
            access_point_id: Optional[str] = None,
            sub_organization_name: Optional[str] = None,
            sub_organization_external_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle authentication flow for creating new integrations across all connector categories.

        Steps:
        1. "list_connectors" - Get available connectors (all categories)
        2. "get_auth_flow" - Get authentication flow for selected connector (checks access points and OAuth state)
        3. "configure_oauth" - Configure OAuth details if OAuth is not configured
        4. "build_installation_form" - Generate installation form URL for OAuth flows
        5. "create_integration" - Create integration with provided auth data (non-OAuth flows)

        Args:
            step: The current step in the authentication flow
            connector_name: Name of the connector (e.g., "github", "jira") - optional if connector_id provided
            connector_id: ID of the selected connector
            connector_category: Category/type of connector when multiple connectors have same name (e.g., "TICKETING", "SCM")
            integration_name: User-provided name for the integration
            auth_data: Authentication data (API key, credentials, OAuth config, etc.)
            access_point_id: Selected access point ID for the connector
            sub_organization_name: Sub-organization name for OAuth installation form
            sub_organization_external_key: Sub-organization external key for OAuth installation form
        """
        logger.info(f"connect_agent MCP tool called with step: {step}")

        try:
            headers = extract_headers_from_request()
            logger.info(f"Using headers for API calls: {headers}")

            if step == "list_connectors":
                return await ConnectService.list_all_connectors(headers)

            elif step == "get_auth_flow":
                if not connector_id and not connector_name:
                    return ResponseFormatter.error_response(
                        message="Either connector_id or connector_name is required for get_auth_flow step."
                    )

                # If connector_name provided, get connector_id and connector_type
                connector_type = None
                if connector_name and not connector_id:
                    connector_result = await ConnectService.get_connector_details_by_name(headers, connector_name,
                                                                                          connector_category)

                    if connector_result["status"] == "error":
                        return connector_result
                    elif connector_result["status"] == "multiple_matches":
                        return connector_result
                    else:
                        connector_id = connector_result["connector_id"]
                        connector_type = connector_result["connector_type"]

                # If we have connector_id but no connector_type, get the connector_type
                if connector_id and not connector_type:
                    connector_type = await ConnectService.get_service_type_by_id(headers, connector_id)
                    if not connector_type:
                        return ResponseFormatter.error_response(
                            message=f"Could not determine connector type for connector_id: {connector_id}"
                        )

                return await ConnectService.get_auth_flow_details(headers, connector_id)

            elif step == "configure_oauth":
                if not all([connector_id, access_point_id, auth_data]):
                    return ResponseFormatter.error_response(
                        message="connector_id, access_point_id, and auth_data are required for configure_oauth step"
                    )
                return await ConnectService.configure_oauth_credentials(headers, connector_id, access_point_id,
                                                                        auth_data)

            elif step == "build_installation_form":
                if not all([connector_id, sub_organization_name, sub_organization_external_key]):
                    return ResponseFormatter.error_response(
                        message="connector_id, sub_organization_name, and sub_organization_external_key are required for build_installation_form step"
                    )
                return await ConnectService.build_oauth_installation_form(headers, connector_id, access_point_id,
                                                                          integration_name,
                                                                          sub_organization_name,
                                                                          sub_organization_external_key)

            elif step == "create_integration":
                if not all([connector_id, integration_name, auth_data, access_point_id]):
                    return ResponseFormatter.error_response(
                        message="connector_id, integration_name, auth_data, and access_point_id are required for create_integration step"
                    )

                # Get service type for integration creation
                connector_type = await ConnectService.get_service_type_by_id(headers, connector_id)

                if not connector_type:
                    return ResponseFormatter.error_response(
                        message=f"Could not determine service type for connector_id: {connector_id}"
                    )

                # Extract provider name from service_name if available
                provider_name = connector_name if connector_name else connector_type[:2] if connector_type else "XX"

                return await ConnectService.create_new_integration(
                    headers, connector_id, integration_name, auth_data,
                    access_point_id, connector_type, provider_name
                )

            else:
                return ResponseFormatter.error_response(
                    message=f"Invalid step: {step}. Valid steps are: list_connectors, get_auth_flow, configure_oauth, build_installation_form, create_integration"
                )

        except Exception as e:
            logger.error(f"Error in connect_agent: {str(e)}")
            return ResponseFormatter.error_response(
                message=str(e),
                error_details=traceback.format_exc()
            )

    async def status_check(
            self,
            sub_organization_external_key: str,
            connector_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check the status of an integration across all service categories.

        Args:
            sub_organization_external_key: The external key of the sub-organization to filter integrations
            connector_type: Optional service type filter (e.g., "TICKETING", "SCM")
        """
        logger.info(
            f"status_check MCP tool called for sub_organization_external_key: {sub_organization_external_key}")
        return await StatusService.check_integration_status(sub_organization_external_key, connector_type)

    # Watch Management Tools
    async def list_watches(
            self,
            integration_id: str,
            correlation_id: Optional[str] = None,
            offset: Optional[int] = 0,
            limit: Optional[int] = 100,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all watches for a specific integration.

        Args:
            integration_id: The ID of the integration
            correlation_id: The unique ID used to trace requests across systems
            offset: Number of records to skip for pagination
            limit: Maximum number of records to return
            sort: Sort criteria (e.g., "name,-createdAt")
        """
        return await WatchService.list_watches(integration_id, correlation_id, offset, limit, sort)

    async def get_watch(
            self,
            integration_id: str,
            watch_id: str,
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a specific watch by ID for a specific integration.

        Args:
            integration_id: The ID of the integration
            watch_id: The ID of the watch to retrieve
            correlation_id: The unique ID used to trace requests across systems
        """
        return await WatchService.get_watch(integration_id, watch_id, correlation_id)

    async def get_watch_internal(
            self,
            watch_id: str,
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a specific watch by ID using internal API endpoint.

        Args:
            watch_id: The ID of the watch to retrieve
            correlation_id: The unique ID used to trace requests across systems
        """
        return await WatchService.get_watch_internal(watch_id, correlation_id)

    async def create_watch(
            self,
            name: str,
            type: str,
            resource_type: str,
            integration_id: str,
            repository_id: Optional[str] = None,
            organization_id: Optional[str] = None,
            config_url: Optional[str] = None,
            config_secured_ssl_required: Optional[bool] = False,
            config_content_type: Optional[str] = "application/json",
            config_secret: Optional[str] = None,
            config_retry_count: Optional[int] = None,
            config_timeout: Optional[int] = None,
            config_headers: Optional[Dict[str, str]] = None,
            description: Optional[str] = None,
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new watch for a specific integration.

        Args:
            name: Name of the watch
            type: Type of watch (HOOK, WEBHOOK, EVENT)
            resource_type: Type of resource being watched (REPOSITORY, PROJECT, ORGANIZATION, etc.)
            integration_id: The ID of the integration
            repository_id: Repository identifier
            organization_id: Organization identifier
            config_url: Webhook URL
            config_secured_ssl_required: Whether SSL is required for the webhook
            config_content_type: Content type of the webhook payload
            config_secret: Secret for webhook signature verification
            config_retry_count: Number of retry attempts for failed deliveries (0-10)
            config_timeout: Timeout in seconds for webhook delivery (1-300)
            config_headers: Additional headers to be sent with the webhook
            description: Description of the watch
            correlation_id: The unique ID used to trace requests across systems
        """
        try:
            resource = WatchResource(
                type=ResourceType(resource_type),
                repository={"id": repository_id} if repository_id else None,
                organization={"id": organization_id} if organization_id else None,
                config=WatchConfig(
                    url=config_url,
                    securedSSLRequired=config_secured_ssl_required,
                    contentType=config_content_type,
                    secret=config_secret,
                    retryCount=config_retry_count,
                    timeout=config_timeout,
                    headers=config_headers
                ) if config_url else None
            )
            watch_request = WatchRequest(
                name=name,
                description=description,
                type=WatchType(type),
                resource=resource
            )

            return await WatchService.create_watch(watch_request, integration_id, correlation_id)

        except Exception as validation_error:
            return ResponseFormatter.error_response(
                message=f"Validation failed: {str(validation_error)}"
            )

    async def update_watch(
            self,
            integration_id: str,
            watch_id: str,
            update_operations: List[Dict[str, Any]],
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a watch using JSON Patch operations.

        Args:
            integration_id: The ID of the integration
            watch_id: The ID of the watch to update
            update_operations: List of JSON Patch operations (op, path, value)
            correlation_id: The unique ID used to trace requests across systems

        Example update_operations:
        [
            {"op": "replace", "path": "/name", "value": "Updated Watch Name"},
            {"op": "replace", "path": "/resource/config/url", "value": "https://new-webhook-url.com"},
            {"op": "replace", "path": "/description", "value": "Updated description"}
        ]
        """
        return await WatchService.update_watch(integration_id, watch_id, update_operations, correlation_id)

    async def delete_watch(
            self,
            integration_id: str,
            watch_id: str,
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete a watch by ID.

        Args:
            integration_id: The ID of the integration
            watch_id: The ID of the watch to delete
            correlation_id: The unique ID used to trace requests across systems
        """
        return await WatchService.delete_watch(integration_id, watch_id, correlation_id)

    # Webhook Management Tools
    async def list_webhooks(
            self,
            correlation_id: Optional[str] = None,
            offset: Optional[int] = 0,
            limit: Optional[int] = 100,
            sort: Optional[str] = None,
            webhook_event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all webhooks.

        Args:
            correlation_id: The unique ID used to trace requests across systems
            offset: Number of records to skip for pagination
            limit: Maximum number of records to return
            sort: Sort criteria (e.g., "name,-createdAt")
            webhook_event_type: Filter by webhook event type (e.g., "PUBLIC")
        """
        return await WebhookService.list_webhooks(correlation_id, offset, limit, sort, webhook_event_type)

    async def get_webhook(
            self,
            webhook_id: str,
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get webhook by identifier.

        Args:
            webhook_id: The ID of the webhook to retrieve
            correlation_id: The unique ID used to trace requests across systems
        """
        return await WebhookService.get_webhook(webhook_id, correlation_id)

    async def create_webhook(
            self,
            name: str,
            url: str,
            description: Optional[str] = None,
            events: Optional[List[str]] = None,
            active: Optional[bool] = True,
            secret: Optional[str] = None,
            ssl_verification: Optional[bool] = True,
            content_type: Optional[str] = "application/json",
            correlation_id: Optional[str] = None,
            request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new webhook.

        Args:
            name: Name of the webhook
            url: Webhook URL
            description: Description of the webhook
            events: List of events to subscribe to
            active: Whether the webhook is active
            secret: Secret for webhook signature verification
            ssl_verification: Whether to verify SSL certificates
            content_type: Content type for webhook payloads
            correlation_id: The unique ID used to trace requests across systems
            request_id: Request ID for tracking
        """
        try:
            webhook_request = WebhookRequest(
                name=name,
                description=description,
                url=url,
                events=events,
                active=active,
                secret=secret,
                ssl_verification=ssl_verification,
                content_type=content_type
            )

            return await WebhookService.create_webhook(webhook_request, correlation_id, request_id)

        except Exception as validation_error:
            return ResponseFormatter.error_response(
                message=f"Validation failed: {str(validation_error)}"
            )

    async def update_webhook(
            self,
            webhook_id: str,
            update_operations: List[Dict[str, Any]],
            correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update webhook by ID using JSON Patch operations.

        Args:
            webhook_id: The ID of the webhook to update
            update_operations: List of JSON Patch operations (op, path, value)
            correlation_id: The unique ID used to trace requests across systems

        Example update_operations:
        [
            {"op": "replace", "path": "/name", "value": "Updated Webhook Name"},
            {"op": "replace", "path": "/url", "value": "https://new-webhook-url.com"},
            {"op": "replace", "path": "/active", "value": false}
        ]
        """
        return await WebhookService.update_webhook(webhook_id, update_operations, correlation_id)

    async def delete_webhook(
            self,
            webhook_id: str,
            correlation_id: Optional[str] = None,
            request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete webhook by identifier.

        Args:
            webhook_id: The ID of the webhook to delete
            correlation_id: The unique ID used to trace requests across systems
            request_id: Request ID for tracking
        """
        return await WebhookService.delete_webhook(webhook_id, correlation_id, request_id)

    async def create_webhook_action(
            self,
            webhook_id: str,
            action: str,
            delivery_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create webhook action (e.g., test, ping, redeliver).

        Args:
            webhook_id: The ID of the webhook
            action: Action to perform (e.g., 'test', 'ping', 'redeliver')
            delivery_id: Delivery ID for redelivery actions
        """
        try:
            action_request = WebhookActionRequest(
                action=action,
                delivery_id=delivery_id
            )

            return await WebhookService.create_webhook_action(webhook_id, action_request)

        except Exception as validation_error:
            return ResponseFormatter.error_response(
                message=f"Validation failed: {str(validation_error)}"
            )

    # ---------- PLATFORM-WIDE LISTING TOOLS ----------

    async def list_all_available_connectors(self) -> Dict[str, Any]:
        """
        Get list of all available connectors across all integration categories.

        This tool aggregates connectors from all categories (SCM, PCR, Ticketing, etc.)
        and returns them grouped by category. Automatically filtered by the user's
        organization/suborganization from request headers.

        Returns:
            Dictionary containing:
            - connectors: List of all unique connectors
            - connectorsByCategory: Connectors grouped by category
            - totalCount: Total number of connectors
            - categoryCount: Number of categories with connectors
            - categories: List of category names

        Example Response:
            {
                "status": "success",
                "message": "Found 15 connectors across 5 categories",
                "data": {
                    "connectors": [
                        {
                            "name": "github",
                            "displayName": "GitHub",
                            "type": "SCM",
                            "category": "SCM",
                            "description": "GitHub source control",
                            "serviceId": "uuid"
                        },
                        ...
                    ],
                    "connectorsByCategory": {
                        "SCM": [...],
                        "PCR": [...],
                        "TICKETING": [...]
                    },
                    "totalCount": 15,
                    "categoryCount": 5,
                    "categories": ["SCM", "PCR", "TICKETING", "OBSERVABILITY", "STORAGE"]
                }
            }
        """
        logger.info("MCP tool: list_all_available_connectors called")
        return await PlatformListingService.list_all_available_connectors()

    async def list_all_available_integrations(
            self,
            connector: Optional[str] = None,
            category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get list of all integrations across all categories, optionally filtered by connector or category.

        This tool aggregates integrations from all categories and allows filtering by:
        - connector: Filter by specific connector name (e.g., "github", "jira")
        - category: Filter by category type (e.g., "SCM", "TICKETING")

        Automatically filtered by the user's organization/suborganization from request headers.

        Args:
            connector: Optional connector name to filter by (e.g., "github", "jira")
            category: Optional category to filter by (e.g., "SCM", "TICKETING", "PCR")

        Returns:
            Dictionary containing:
            - integrations: List of all integrations
            - integrationsByCategory: Integrations grouped by category
            - integrationsByConnector: Integrations grouped by connector
            - totalCount: Total number of integrations
            - categoryCount: Number of categories
            - connectorCount: Number of unique connectors
            - categories: List of category names
            - connectors: List of connector names

        Example Response:
            {
                "status": "success",
                "message": "Found 25 integrations",
                "data": {
                    "integrations": [
                        {
                            "id": "uuid",
                            "name": "GH_MYPR_1234567890",
                            "connector": "github",
                            "connectorDisplayName": "GitHub",
                            "type": "SCM",
                            "category": "SCM",
                            "state": "ACTIVE",
                            "createdAt": "2025-10-22T10:00:00Z",
                            "subOrganization": {...}
                        },
                        ...
                    ],
                    "integrationsByCategory": {
                        "SCM": [...],
                        "TICKETING": [...]
                    },
                    "integrationsByConnector": {
                        "github": [...],
                        "jira": [...]
                    },
                    "totalCount": 25,
                    "categoryCount": 4,
                    "connectorCount": 8,
                    "categories": ["SCM", "PCR", "TICKETING", "STORAGE"],
                    "connectors": ["github", "gitlab", "jira", "servicenow", ...]
                }
            }
        """
        logger.info(f"MCP tool: list_all_available_integrations called - connector: {connector}, category: {category}")
        return await PlatformListingService.list_all_available_integrations(connector, category)