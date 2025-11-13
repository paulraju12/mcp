import time
import traceback
from typing import Dict, Any, Optional, List
import structlog
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request
from tempory.core import settings
from ..models.platform import APIResponse
import json

logger = structlog.getLogger(__name__)


class ConnectService:
    """Service for handling integration connection and authentication flows"""

    @staticmethod
    async def list_all_connectors(headers: Dict[str, str]) -> Dict[str, Any]:
        """Get list of all available connectors for integration creation."""
        logger.info("Fetching all available connectors")

        try:
            headers = extract_headers_from_request()
            url = f"{settings.integration_mgr_base_url}/api/v1/services"
            params = {"limit": 100}
            response = await http_client_service.make_request("get", url, headers, params=params)

            # Handle different response formats
            if isinstance(response, dict):
                connectors_data = response.get("data", [])
            elif isinstance(response, list):
                connectors_data = response
            else:
                connectors_data = []

            connectors = []
            connector_types = set()

            for connector in connectors_data:
                connector_info = {
                    "id": connector.get("id"),
                    "name": connector.get("name", "").lower(),
                    "display_name": connector.get("displayName", connector.get("name", "")),
                    "description": connector.get("description", ""),
                    "type": connector.get("type", ""),
                    "supported_types": connector.get("supportedTypes", [])
                }
                connectors.append(connector_info)
                if connector.get("type"):
                    connector_types.add(connector.get("type"))

            return ResponseFormatter.success_response(
                message=f"Found {len(connectors)} available connectors across {len(connector_types)} categories",
                data={
                    "connectors": connectors,
                    "connector_categories": list(connector_types),
                    "next_step": "get_auth_flow",
                    "instructions": "Select a connector by providing its 'id' or 'name' to get authentication requirements"
                }
            )

        except Exception as e:
            logger.error(f"Error fetching connectors: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to fetch connectors: {str(e)}"
            )

    @staticmethod
    async def get_connector_details_by_name(headers: Dict[str, str], connector_name: str,
                                          connector_category: Optional[str] = None) -> Dict[str, Any]:
        """Get connector details by name, handling multiple matches by asking for category selection."""
        logger.info(f"Searching for connector details for connector_name: {connector_name}, category: {connector_category}")

        try:
            url = f"{settings.integration_mgr_base_url}/api/v1/services"
            params = {"limit": 100}
            response = await http_client_service.make_request("get", url, headers, params=params)

            # Handle different response formats
            if isinstance(response, dict):
                connectors_data = response.get("data", [])
            elif isinstance(response, list):
                connectors_data = response
            else:
                connectors_data = []

            # Find all connectors that match the name
            matching_connectors = []
            for connector in connectors_data:
                if connector.get("name", "").lower() == connector_name.lower():
                    matching_connectors.append({
                        "id": connector.get("id"),
                        "name": connector.get("name", ""),
                        "type": connector.get("type", ""),
                        "display_name": connector.get("displayName", connector.get("name", "")),
                        "description": connector.get("description", ""),
                        "supported_types": connector.get("supportedTypes", [])
                    })

            if len(matching_connectors) == 0:
                logger.warning(f"Connector '{connector_name}' not found in connectors list")
                return ResponseFormatter.error_response(
                    message=f"Connector '{connector_name}' not found. Please call list_connectors to see available options."
                )
            elif len(matching_connectors) == 1:
                connector = matching_connectors[0]
                logger.info(f"Found single connector match: {connector['id']} ({connector['type']})")
                return {
                    "status": "success",
                    "connector_id": connector["id"],
                    "connector_type": connector["type"]
                }
            else:
                if connector_category:
                    for connector in matching_connectors:
                        if connector["type"].upper() == connector_category.upper():
                            logger.info(
                                f"Found matching connector: {connector['id']} for {connector_name} ({connector_category})")
                            return {
                                "status": "success",
                                "connector_id": connector["id"],
                                "connector_type": connector["type"]
                            }

                    available_categories = [s["type"] for s in matching_connectors]
                    return ResponseFormatter.error_response(
                        message=f"Connector '{connector_name}' with category '{connector_category}' not found. Available categories: {available_categories}"
                    )
                else:
                    return {
                        "status": "multiple_matches",
                        "message": f"Found multiple connectors with name '{connector_name}'. Please specify the category you want to proceed with.",
                        "matching_connectors": matching_connectors,
                        "instructions": "Call get_auth_flow again with both connector_name and connector_category parameters",
                        "usage_example": {
                            "step": "get_auth_flow",
                            "connector_name": connector_name,
                            "connector_category": "TICKETING"
                        },
                        "available_categories": list(set([s["type"] for s in matching_connectors if s["type"]]))
                    }

        except Exception as e:
            logger.error(f"Error fetching connector details for {connector_name}: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to fetch connector details: {str(e)}"
            )

    @staticmethod
    async def get_service_type_by_id(headers: Dict[str, str], service_id: str) -> Optional[str]:
        """Get service type by service ID."""
        logger.info(f"Getting service type for service_id: {service_id}")

        try:
            url = f"{settings.integration_mgr_base_url}/api/v1/services/{service_id}"
            response = await http_client_service.make_request("get", url, headers)

            # Handle different response formats
            if isinstance(response, dict):
                service_type = response.get("type")
            else:
                service_type = None

            logger.info(f"Service {service_id} has type: {service_type}")
            return service_type

        except Exception as e:
            logger.error(f"Error fetching service type for {service_id}: {str(e)}")
            return None

    @staticmethod
    async def get_auth_flow_details(headers: Dict[str, str], service_id: str) -> Dict[str, Any]:
        """Get authentication flow details for a specific service by checking access points. only proceed with the available accesstypeconfigs do not choose alternate typeconfigs if that is not present in the api response"""

        logger.info(f"Fetching auth flow details for service: {service_id}")

        try:
            url = f"{settings.integration_mgr_base_url}/api/v1/services/{service_id}/accessPoints"
            response = await http_client_service.make_request("get", url, headers)

            # Handle different response formats
            if isinstance(response, dict):
                access_points_data = response.get("data", [])
            elif isinstance(response, list):
                access_points_data = response
            else:
                access_points_data = []

            access_points = []
            oauth_access_point = None

            for ap in access_points_data:
                # Extract dynamic field configurations based on flow type
                flow_type = ap.get("accessPointTypeConfig", {}).get("type")
                dynamic_fields = ConnectService.extract_dynamic_fields(ap, flow_type)

                access_point_info = {
                    "id": ap.get("id"),
                    "label": ap.get("label", ""),
                    "description": ap.get("description", ""),
                    "type": ap.get("type"),
                    "flow_type": flow_type,
                    "state": ap.get("state", ""),
                    "required_fields": dynamic_fields.get("required_fields", []),
                    "optional_fields": dynamic_fields.get("optional_fields", []),
                    "field_configs": dynamic_fields.get("field_configs", []),
                    "auth_data_template": dynamic_fields.get("auth_data_template", {}),
                    "oAuthDetails": ap.get("oAuthDetails", {})
                }
                access_points.append(access_point_info)

                # Check for OAuth access point
                if flow_type == "OAUTH_FLW":
                    oauth_access_point = access_point_info

            # Handle OAuth flow logic
            if oauth_access_point:
                return await ConnectService.handle_oauth_flow_check(oauth_access_point, service_id, access_points)

            # Handle non-OAuth flows with dynamic fields
            return await ConnectService.handle_non_oauth_flows_dynamic(access_points, service_id)

        except Exception as e:
            logger.error(f"Error fetching auth flow details: {str(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            return ResponseFormatter.error_response(
                message=f"Failed to fetch authentication flow details: {str(e)}"
            )

    @staticmethod
    def extract_dynamic_fields(access_point: Dict[str, Any], flow_type: str) -> Dict[str, Any]:
        """Extract dynamic field configurations from access point based on flow type."""
        result = {
            "required_fields": [],
            "optional_fields": [],
            "field_configs": [],
            "auth_data_template": {}
        }

        try:
            # Different flow types have different field configuration locations
            field_configs = []

            if flow_type == "OAUTH_FLW":
                # Extract OAuth specific configurations
                oauth_details = access_point.get("oAuthDetails", {})
                auth_process_config = oauth_details.get("authorizationProcessConfig", {})
                step_configs = auth_process_config.get("stepConfigs", [])

                for step_config in step_configs:
                    field_type_configs = step_config.get("fieldTypeConfigs", [])
                    field_configs.extend(field_type_configs)

            if flow_type == "OAUTH_PASSWORD_FLW":
                oauth_details = access_point.get("oAuthPasswordDetails", {})
                auth_process_config = oauth_details.get("authorizationProcessConfig", {})
                step_configs = auth_process_config.get("stepConfigs", [])

                for step_config in step_configs:
                    field_type_configs = step_config.get("fieldTypeConfigs", [])
                    field_configs.extend(field_type_configs)

            elif flow_type == "APIKEY_FLW":
                # Look for API key specific configurations
                apikey_details = access_point.get("apiKey", {})
                auth_process_config = apikey_details.get("authorizationProcessConfig", {})
                step_configs = auth_process_config.get("stepConfigs", [])

                for step_config in step_configs:
                    field_type_configs = step_config.get("fieldTypeConfigs", [])
                    field_configs.extend(field_type_configs)

            elif flow_type == "CREDENTIALS_FLW":
                # Look for credentials specific configurations
                credentials_details = access_point.get("credentialsDetails", {})
                auth_process_config = credentials_details.get("authorizationProcessConfig", {})
                step_configs = auth_process_config.get("stepConfigs", [])

                for step_config in step_configs:
                    field_type_configs = step_config.get("fieldTypeConfigs", [])
                    field_configs.extend(field_type_configs)

            elif flow_type == "APP_FLW":
                # Look for app specific configurations
                app_details = access_point.get("appDetails", {})
                auth_process_config = app_details.get("authorizationProcessConfig", {})
                step_configs = auth_process_config.get("stepConfigs", [])

                for step_config in step_configs:
                    field_type_configs = step_config.get("fieldTypeConfigs", [])
                    field_configs.extend(field_type_configs)

            # Process field configurations
            for field_config in field_configs:
                field_property = field_config.get("property", "").strip("/")  # Remove leading slash
                field_label = field_config.get("label", "")
                field_type = field_config.get("type", "TEXT")
                field_description = field_config.get("description", "")
                is_required = field_config.get("required", False)
                placeholder = field_config.get("placeholder", "")

                field_info = {
                    "property": field_property,
                    "label": field_label,
                    "type": field_type,
                    "description": field_description,
                    "placeholder": placeholder,
                    "required": is_required
                }

                result["field_configs"].append(field_info)

                if is_required:
                    result["required_fields"].append(field_property)
                else:
                    result["optional_fields"].append(field_property)

                # Add to auth data template
                result["auth_data_template"][field_property] = f"your_{field_property.lower()}"

        except Exception as e:
            logger.error(f"Error extracting dynamic fields for flow type {flow_type}: {str(e)}")
            # Fallback to basic field structure
            if flow_type == "OAUTH_FLW":
                result = {
                    "required_fields": ["clientId", "clientSecret"],
                    "optional_fields": [],
                    "field_configs": [
                        {"property": "clientId", "label": "Client ID", "required": True,
                         "description": "OAuth Client ID"},
                        {"property": "clientSecret", "label": "Client Secret", "required": True,
                         "description": "OAuth Client Secret"}
                    ],
                    "auth_data_template": {"clientId": "your_client_id", "clientSecret": "your_client_secret"}
                }
            else:
                result = {
                    "required_fields": ["field1"],
                    "optional_fields": [],
                    "field_configs": [{"property": "field1", "label": "Authentication Field", "required": True}],
                    "auth_data_template": {"field1": "your_auth_value"}
                }

        return result

    @staticmethod
    async def handle_oauth_flow_check(oauth_access_point: Dict[str, Any], service_id: str,
                                      all_access_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle OAuth flow - check if configured and provide appropriate next steps with user choice."""
        logger.info(f"Handling OAuth flow for access point: {oauth_access_point['id']}")

        oauth_state = oauth_access_point.get("state", "")
        oauth_details = oauth_access_point.get("oAuthDetails", {})
        flow_type = oauth_access_point.get("flow_type", "OAUTH_FLW")

        # Extract dynamic field configurations for OAuth
        dynamic_fields = ConnectService.extract_dynamic_fields(oauth_access_point, flow_type)
        required_fields = dynamic_fields.get("required_fields", [])
        field_configs = dynamic_fields.get("field_configs", [])
        auth_data_template = dynamic_fields.get("auth_data_template", {})

        # Check OAuth state and handle accordingly
        if oauth_state == "CONFIGURED":
            return await ConnectService._handle_configured_oauth(
                oauth_access_point, service_id, oauth_details,
                field_configs, required_fields, auth_data_template
            )
        elif oauth_state == "READY_TO_BE_CONFIGURED":
            return await ConnectService._handle_ready_to_be_configured_oauth(
                oauth_access_point, service_id, oauth_details,
                field_configs, required_fields, auth_data_template
            )
        elif oauth_state in ["NOT_CONFIGURED", "READY", "PENDING", ""]:
            return await ConnectService._handle_unconfigured_oauth(
                oauth_access_point, service_id, oauth_details,
                field_configs, required_fields, auth_data_template
            )
        else:
            return ResponseFormatter.error_response(
                message=f"OAuth access point is in unexpected state: {oauth_state}",
                error_details={
                    "access_point_id": oauth_access_point["id"],
                    "current_state": oauth_state,
                    "supported_states": ["CONFIGURED", "READY_TO_BE_CONFIGURED", "NOT_CONFIGURED", "READY", "PENDING"]
                }
            )

    @staticmethod
    async def _handle_ready_to_be_configured_oauth(oauth_access_point, service_id, oauth_details,
                                                   field_configs, required_fields, auth_data_template):
        """Handle OAuth that is ready to be configured but needs portal configuration first."""
        service_name = oauth_access_point.get("label", "Unknown Service")

        return {
            "status": "oauth_needs_portal_configuration",
            "message": f"OAuth access point for {service_name} is ready to be configured but requires setup in the Unizo portal first.",
            "access_point": oauth_access_point,
            "current_state": "READY_TO_BE_CONFIGURED",
            "portal_configuration_required": True,
            "instructions": {
                "step_1": "Visit the Unizo portal at https://app.unizo.ai/",
                "step_2": "Navigate to the 'Connectors' section",
                "step_3": f"Find the appropriate category and locate your {service_name} service",
                "step_4": "Complete the OAuth configuration in the portal",
                "step_5": "Once configured, return here and call get_auth_flow again to verify the configuration"
            },
            "portal_url": "https://app.unizo.ai/",
            "next_step_after_portal_config": "get_auth_flow",
            "verification_example": {
                "step": "get_auth_flow",
                "connector_id": service_id,
                "message": "Call this again after completing portal configuration to verify CONFIGURED state"
            },
            "field_configurations": field_configs,
            "required_fields": required_fields,
            "note": "After portal configuration, the state should change to 'CONFIGURED' and you can proceed with build_installation_form"
        }

    @staticmethod
    async def _handle_configured_oauth(oauth_access_point, service_id, oauth_details,
                                       field_configs, required_fields, auth_data_template):
        """Handle OAuth that is already configured."""
        current_oauth_details = {}
        for field_config in field_configs:
            field_property = field_config["property"]
            current_value = oauth_details.get(field_property, "")

            # Mask sensitive fields in response
            if "secret" in field_property.lower() or "password" in field_property.lower():
                current_oauth_details[field_property] = "***" if current_value else "Not configured"
            else:
                current_oauth_details[field_property] = current_value or "Not configured"

        return {
            "status": "oauth_configured_ready_for_installation",
            "message": "OAuth access point is fully configured. You can now proceed to generate the installation form.",
            "access_point": oauth_access_point,
            "current_oauth_details": current_oauth_details,
            "field_configurations": field_configs,
            "required_fields": required_fields,
            "current_state": "CONFIGURED",
            "next_step": "build_installation_form",
            "instructions": "OAuth is ready to use. Provide sub_organization details to generate the installation form URL",
            "usage_example": {
                "step": "build_installation_form",
                "connector_id": service_id,
                "access_point_id": oauth_access_point["id"],
                "integration_name": "My Integration",
                "sub_organization_name": "MyCompany",
                "sub_organization_external_key": "company-external-key-123"
            }
        }

    @staticmethod
    async def _handle_unconfigured_oauth(oauth_access_point, service_id, oauth_details,
                                         field_configs, required_fields, auth_data_template):
        """Handle OAuth that needs configuration."""
        missing_fields = []
        current_oauth_details = {}

        for field_config in field_configs:
            field_property = field_config["property"]
            current_value = oauth_details.get(field_property, "")

            if field_config.get("required", False) and not current_value:
                missing_fields.append(field_property)

            # Mask sensitive fields in response
            if "secret" in field_property.lower() or "password" in field_property.lower():
                current_oauth_details[field_property] = "***" if current_value else "Not configured"
            else:
                current_oauth_details[field_property] = current_value or "Not configured"

        return {
            "status": "oauth_needs_configuration",
            "message": f"OAuth access point needs configuration. Missing required fields: {', '.join(missing_fields) if missing_fields else 'None'}",
            "access_point": oauth_access_point,
            "current_oauth_details": current_oauth_details,
            "field_configurations": field_configs,
            "required_fields": required_fields,
            "auth_data_template": auth_data_template,
            "next_step": "configure_oauth",
            "instructions": f"Provide OAuth credentials in auth_data for the '{oauth_access_point['label']}' service according to the field_configurations",
            "usage_example": {
                "step": "configure_oauth",
                "connector_id": service_id,
                "access_point_id": oauth_access_point["id"],
                "auth_data": auth_data_template
            }
        }

    @staticmethod
    async def handle_non_oauth_flows_dynamic(access_points: List[Dict[str, Any]], service_id: str) -> Dict[str, Any]:
        """Handle non-OAuth authentication flows using dynamic field configurations."""
        logger.info("Handling non-OAuth authentication flows with dynamic fields")

        auth_options = []

        for ap in access_points:
            flow_type = ap.get("flow_type", "")
            label = ap.get("label", "")
            field_configs = ap.get("field_configs", [])
            required_fields = ap.get("required_fields", [])
            optional_fields = ap.get("optional_fields", [])
            auth_data_template = ap.get("auth_data_template", {})

            auth_option = {
                "access_point_id": ap["id"],
                "label": label,
                "flow_type": flow_type,
                "description": ap.get("description", ""),
                "state": ap.get("state", ""),
                "required_fields": required_fields,
                "optional_fields": optional_fields,
                "field_configurations": field_configs,
                "auth_data_template": auth_data_template
            }

            # Generate instructions based on dynamic fields
            if field_configs:
                required_field_labels = [fc["label"] for fc in field_configs if fc.get("required")]
                optional_field_labels = [fc["label"] for fc in field_configs if not fc.get("required")]

                instructions = f"Provide authentication data for {label}.\n"

                if required_field_labels:
                    instructions += f"Required fields: {', '.join(required_field_labels)}\n"
                if optional_field_labels:
                    instructions += f"Optional fields: {', '.join(optional_field_labels)}\n"

                instructions += "Field descriptions:\n"
                for fc in field_configs:
                    desc_text = fc.get("description", fc.get("label", ""))
                    instructions += f"- {fc['property']}: {desc_text}\n"

                auth_option["instructions"] = instructions.strip()
            else:
                # Fallback instructions
                auth_option[
                    "instructions"] = f"Provide authentication details for {label}. Check service documentation for required fields."

            auth_options.append(auth_option)

        return {
            "status": "auth_options_available",
            "message": f"Found {len(auth_options)} authentication options with dynamic field configurations",
            "auth_options": auth_options,
            "next_step": "create_integration",
            "instructions": "Select an access point and provide the required authentication data according to the field_configurations",
            "usage_example": {
                "step": "create_integration",
                "connector_id": service_id,
                "integration_name": "MyIntegration",
                "access_point_id": "select_from_auth_options_above",
                "auth_data": "use_auth_data_template_from_selected_option"
            }
        }

    @staticmethod
    async def configure_oauth_credentials(
            headers: Dict[str, str],
            service_id: str,
            access_point_id: str,
            auth_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure OAuth credentials for an access point using PATCH request with proper JSON format."""
        logger.info(f"Configuring OAuth credentials for service: {service_id}, access_point: {access_point_id}")

        try:
            # First, get the access point details to understand required fields
            ap_url = f"{settings.integration_mgr_base_url}/api/v1/services/{service_id}/accessPoints"
            ap_response = await http_client_service.make_request("get", ap_url, headers)

            # Handle different response formats
            if isinstance(ap_response, dict):
                access_points = ap_response.get("data", [])
            elif isinstance(ap_response, list):
                access_points = ap_response
            else:
                access_points = []

            selected_ap = None
            for ap in access_points:
                if ap.get("id") == access_point_id:
                    selected_ap = ap
                    break

            if not selected_ap:
                return ResponseFormatter.error_response(
                    message=f"Access point {access_point_id} not found for service {service_id}"
                )

            # Validate this is an OAuth flow
            flow_type = selected_ap.get("accessPointTypeConfig", {}).get("type")
            if flow_type not in ["OAUTH_FLW", "OAUTH_PASSWORD_FLW"]:
                return ResponseFormatter.error_response(
                    message=f"Access point is not an OAuth flow. Flow type: {flow_type}",
                    error_details={"expected_flow_types": ["OAUTH_FLW", "OAUTH_PASSWORD_FLW"]}
                )

            # Extract dynamic field configurations for OAuth
            dynamic_fields = ConnectService.extract_dynamic_fields(selected_ap, flow_type)
            required_fields = dynamic_fields.get("required_fields", [])
            field_configs = dynamic_fields.get("field_configs", [])

            # Validate required fields are provided
            missing_fields = [field for field in required_fields if not auth_data.get(field)]
            if missing_fields:
                return ResponseFormatter.error_response(
                    message=f"Missing required OAuth fields: {missing_fields}",
                    error_details={
                        "required_fields": required_fields,
                        "provided_fields": list(auth_data.keys()),
                        "field_descriptions": [
                            {
                                "property": fc["property"],
                                "label": fc["label"],
                                "description": fc.get("description", ""),
                                "required": fc.get("required", False)
                            }
                            for fc in field_configs
                        ]
                    }
                )

            # Generate redirect URL if not provided
            if "redirectUrl" not in auth_data:
                auth_data["redirectUrl"] = f"{settings.integration_mgr_base_url}/callback/oauth"

            # Build operations payload with correct path structure based on flow type
            operations_payload = []
            configured_fields = {}

            # Determine the correct base path for this flow type
            if flow_type == "OAUTH_FLW":
                base_path = "/oAuthDetails"
            elif flow_type == "OAUTH_PASSWORD_FLW":
                base_path = "/oAuthPasswordDetails"
            else:
                base_path = "/oAuthDetails"  # fallback

            for field_name, field_value in auth_data.items():
                field_path = f"{base_path}/{field_name}"
                operations_payload.append({
                    "value": field_value,
                    "path": field_path,
                    "op": "replace"
                })

                # Don't log sensitive values
                if "secret" in field_name.lower() or "password" in field_name.lower():
                    configured_fields[field_name] = "***"
                else:
                    configured_fields[field_name] = field_value

            # Use the existing http_client_service for consistency
            url = f"{settings.integration_mgr_base_url}/api/v1/services/{service_id}/accessPoints/{access_point_id}"

            logger.info(f"Sending PATCH request to: {url}")
            logger.info(f"Operations payload: {operations_payload}")
            logger.info(f"Configuring fields: {list(configured_fields.keys())}")

            # FIXED: Use json_data instead of form_data
            response = await http_client_service.make_request(
                "patch", url, headers, json_data=operations_payload
            )

            logger.info(f"OAuth configuration successful")

            return {
                "status": "success",
                "message": "OAuth credentials configured successfully using dynamic field configuration",
                "configured_details": configured_fields,
                "configured_field_count": len(auth_data),
                "field_configuration": {
                    "required_fields_configured": [f for f in required_fields if f in auth_data],
                    "total_fields_configured": len(auth_data)
                },
                "next_step": "build_installation_form",
                "instructions": "OAuth is now configured. Provide sub_organization details to generate the installation form URL",
                "usage_example": {
                    "step": "build_installation_form",
                    "connector_id": service_id,
                    "access_point_id": access_point_id,
                    "integration_name": "My Integration",
                    "sub_organization_name": "MyCompany",
                    "sub_organization_external_key": "company-key-123"
                }
            }

        except Exception as e:
            logger.error(f"Error configuring OAuth credentials: {str(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            return ResponseFormatter.error_response(
                message=f"Failed to configure OAuth credentials: {str(e)}",
                error_details={
                    "connector_id": service_id,
                    "access_point_id": access_point_id,
                    "provided_auth_fields": list(auth_data.keys()) if auth_data else [],
                    "error_traceback": traceback.format_exc()
                }
            )

    @staticmethod
    async def build_oauth_installation_form(
            headers: Dict[str, str],
            service_id: str,
            access_point_id: str,
            integration_name: str,
            sub_organization_name: str,
            sub_organization_external_key: str
    ) -> Dict[str, Any]:
        """Build OAuth installation form URL for user authorization."""
        logger.info(f"Building OAuth installation form for service: {service_id}, access_point: {access_point_id}")

        try:
            url = f"{settings.integration_mgr_base_url}/api/v1/services/{service_id}/oauth/buildInstallationFormUrl"

            # Prepare query parameters
            params = {
                "successUrl": f"https://app.unizo.ai/integrationSuccessful",
                "failureUrl": f"https://app.unizo.ai/integrationFailed",
                "subOrganizationName": sub_organization_name,
                "subOrganizationExternalKey": sub_organization_external_key
            }

            # Make GET request with query parameters
            response = await http_client_service.make_request("get", url, headers=headers, params=params)

            # Handle different response formats
            if isinstance(response, dict):
                form_url = response.get("formUrl", "")
            else:
                form_url = ""

            if not form_url:
                return ResponseFormatter.error_response(
                    message="Failed to generate installation form URL - no form URL returned",
                    error_details={
                        "connector_id": service_id,
                        "access_point_id": access_point_id,
                        "response_type": type(response).__name__,
                        "response_keys": list(response.keys()) if isinstance(response, dict) else "Not a dict"
                    }
                )

            return {
                "status": "success",
                "message": "OAuth installation form URL generated successfully",
                "form_url": form_url,
                "integration_details": {
                    "name": integration_name,
                    "connector_id": service_id,
                    "access_point_id": access_point_id
                },
                "sub_organization_details": {
                    "name": sub_organization_name,
                    "external_key": sub_organization_external_key
                },
                "instructions": [
                    "1. Visit the form_url to complete OAuth authorization",
                    "2. After successful authorization, the integration will be created automatically",
                    "3. Use status_check tool with the sub_organization_external_key to verify integration creation",
                    "4. No need to call create_integration - OAuth flow handles integration creation"
                ],
                "next_actions": {
                    "user_action": "Visit form_url and complete OAuth authorization",
                    "verification": {
                        "tool": "status_check",
                        "params": {
                            "sub_organization_external_key": sub_organization_external_key
                        }
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error building OAuth installation form: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to build OAuth installation form: {str(e)}",
                error_details={
                    "connector_id": service_id,
                    "access_point_id": access_point_id,
                    "integration_name": integration_name,
                    "sub_organization_name": sub_organization_name,
                    "sub_organization_external_key": sub_organization_external_key
                }
            )

    @staticmethod
    async def create_new_integration(
            headers: Dict[str, str],
            service_id: str,
            integration_name: str,
            auth_data: Dict[str, Any],
            access_point_id: str,
            service_type: str,
            provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new integration with dynamic field validation (non-OAuth flows)."""
        logger.info(f"Creating new integration: {integration_name} for service: {service_id}")

        try:
            # Get access point details to determine flow type and field requirements
            ap_url = f"{settings.integration_mgr_base_url}/api/v1/services/{service_id}/accessPoints"
            ap_response = await http_client_service.make_request("get", ap_url, headers)

            # Handle different response formats
            if isinstance(ap_response, dict):
                access_points = ap_response.get("data", [])
            elif isinstance(ap_response, list):
                access_points = ap_response
            else:
                access_points = []

            selected_ap = None
            for ap in access_points:
                if ap.get("id") == access_point_id:
                    selected_ap = ap
                    break

            if not selected_ap:
                return ResponseFormatter.error_response(
                    message=f"Access point {access_point_id} not found for service {service_id}"
                )

            flow_type = selected_ap.get("accessPointTypeConfig", {}).get("type")

            # Prevent OAuth flows from using this endpoint
            if flow_type == "OAUTH_FLW":
                return ResponseFormatter.error_response(
                    message="OAuth flows should use build_installation_form instead of create_integration. OAuth integrations are created automatically after user authorization.",
                    error_details={"correct_flow": "Use build_installation_form step for OAuth authentication"}
                )

            # Extract dynamic field configurations
            dynamic_fields = ConnectService.extract_dynamic_fields(selected_ap, flow_type)
            field_configs = dynamic_fields.get("field_configs", [])
            required_fields = dynamic_fields.get("required_fields", [])

            # Validate required fields are provided
            missing_fields = [field for field in required_fields if not auth_data.get(field)]
            if missing_fields:
                return ResponseFormatter.error_response(
                    message=f"Missing required fields: {missing_fields}",
                    error_details={
                        "required_fields": required_fields,
                        "provided_fields": list(auth_data.keys()),
                        "field_descriptions": [
                            {
                                "property": fc["property"],
                                "label": fc["label"],
                                "description": fc.get("description", ""),
                                "required": fc.get("required", False)
                            }
                            for fc in field_configs
                        ]
                    }
                )

            # Generate provider name if not provided
            if not provider_name:
                provider_name = service_type[:2] if service_type else "XX"

            # Generate unique integration name
            formatted_name = ConnectService.generate_integration_name(provider_name, integration_name)

            # Build integration payload using dynamic fields
            payload = ConnectService.build_integration_payload_dynamic(
                formatted_name, service_id, selected_ap, auth_data,
                integration_name, service_type, field_configs, headers
            )

            # Create integration
            url = f"{settings.integration_mgr_base_url}/api/v1/integrations"
            logger.info(f"About to create integration with payload: {json.dumps(payload, indent=2)}")
            logger.info(f"Making POST request to: {url}")
            response = await http_client_service.make_request("post", url, headers, json_data=payload)

            # Handle different response formats
            if isinstance(response, dict):
                integration_response = response
            else:
                integration_response = {}

            return {
                "status": "success",
                "message": f"Integration '{formatted_name}' created successfully using dynamic field configuration",
                "integration": {
                    "id": integration_response.get("id"),
                    "name": formatted_name,
                    "connector_id": service_id,
                    "integration_name": integration_name,
                    "type": service_type,
                    "status": integration_response.get("state", "ACTIVE"),
                    "created_at": integration_response.get("createdAt"),
                    "flow_type": flow_type,
                    "access_point_id": access_point_id,
                    "configured_fields": list(auth_data.keys())
                },
                "field_configuration": {
                    "required_fields_used": [f for f in required_fields if f in auth_data],
                    "optional_fields_used": [f for f in auth_data.keys() if f not in required_fields],
                    "total_fields_configured": len(auth_data)
                },
                "next_steps": [
                    "Integration is now ready to use",
                    "You can now use other MCP tools with this integration",
                    "Use list_services and list_integrations to explore available options"
                ]
            }

        except Exception as e:
            logger.error(f"Error creating integration: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to create integration: {str(e)}",
                error_details={
                    "connector_id": service_id,
                    "integration_name": integration_name,
                    "access_point_id": access_point_id,
                    "flow_type": flow_type if 'flow_type' in locals() else "unknown",
                    "provided_auth_fields": list(auth_data.keys()) if auth_data else []
                }
            )

    @staticmethod
    def generate_integration_name(provider_name: str, user_name: str) -> str:
        """
        Generate unique integration name in the required format:
        [Provider 2 chars][Integration name 4 chars][Random 4 digits]

        Example: provider="jira", user_name="MyProject" -> "JIMYPR1234"
        """
        try:
            # Get first 2 letters of provider (uppercase)
            provider_prefix = provider_name[:2].upper() if len(provider_name) >= 2 else provider_name.upper().ljust(2,
                                                                                                                    'X')

            # Get first 4 letters of integration name (uppercase, remove spaces, pad if needed)
            integration_clean = user_name.replace(' ', '').replace('-', '').replace('_', '')
            integration_prefix = integration_clean[:4].upper()
            if len(integration_prefix) < 4:
                integration_prefix = integration_prefix.ljust(4, 'X')

            # Generate random 4-digit number
            random_suffix = str(int(time.time() * 1000))

            result = f"{provider_prefix}_{integration_prefix}_{random_suffix}"
            logger.info(
                f"Generated integration name: {result} (Provider: {provider_name} -> {provider_prefix}, Integration: {user_name} -> {integration_prefix}, Random: {random_suffix})")

            return result

        except Exception as e:
            logger.error(f"Error generating integration name: {e}")
            # Fallback to timestamp-based naming
            timestamp = str(int(time.time() * 1000))[-4:]
            fallback = f"XX{user_name[:4].upper()}{timestamp}"
            logger.info(f"Using fallback integration name: {fallback}")
            return fallback

    @staticmethod
    def build_integration_payload_dynamic(
            integration_name: str,
            service_id: str,
            access_point: Dict[str, Any],
            auth_data: Dict[str, Any],
            user_integration_name: str,
            service_type: str,
            field_configs: List[Dict[str, Any]],
            headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Build integration payload using dynamic field configurations."""
        flow_type = access_point.get("accessPointTypeConfig", {}).get("type")

        logger.info(f"Building payload for flow_type: {flow_type}")
        logger.info(f"Auth data received: {auth_data}")
        logger.info(f"Field configs: {field_configs}")

        # Get suborganizationId from headers
        suborganization_id = headers.get("suborganizationId")
        if not suborganization_id:
            logger.warning("suborganizationId not found in headers, falling back to timestamp")
            suborganization_id = f"{int(time.time())}"
        else:
            logger.info(f"Using suborganizationId from headers: {suborganization_id}")

        # Build base payload
        payload = {
            "name": integration_name,
            "type": service_type,
            "subOrganization": {
                "name": f"{user_integration_name.title()}",
                "externalKey": suborganization_id
            },
            "target": {
                "accessPoint": {
                    "type": "SP",
                    "service": {
                        "id": service_id
                    },
                    "accessPointTypeConfig": {
                        "type": flow_type
                    }
                }
            }
        }

        # Validate required fields are present
        required_fields = [fc["property"] for fc in field_configs if fc.get("required")]
        missing_fields = [field for field in required_fields if not auth_data.get(field)]

        if missing_fields:
            raise ValueError(f"Missing required fields for {flow_type}: {missing_fields}")

        # DYNAMIC APPROACH: Use field_configs to determine how to map auth_data
        # This works for ALL flow types without hardcoding specific logic

        logger.info(f"Dynamically mapping {len(auth_data)} auth fields to payload...")

        # Map all provided auth_data fields to the payload
        # The field_configs tell us which fields are expected, so we use that as our guide
        for field_name, field_value in auth_data.items():
            # Find the field config for this field to understand its purpose
            field_config = None
            for fc in field_configs:
                if fc["property"] == field_name:
                    field_config = fc
                    break

            # Add the field to the appropriate location in the payload
            payload["target"]["accessPoint"][field_name] = field_value

            if field_config:
                logger.info(
                    f"Mapped field '{field_name}' ({field_config['label']}) = {'***' if 'secret' in field_name.lower() or 'password' in field_name.lower() or 'token' in field_name.lower() else field_value}")
            else:
                logger.info(
                    f"Mapped field '{field_name}' = {'***' if 'secret' in field_name.lower() or 'password' in field_name.lower() or 'token' in field_name.lower() else field_value}")

        # Special handling for OAuth flows that might need different payload structure
        if flow_type == "OAUTH_FLW":
            logger.info(
                "OAuth flow detected - payload structure should be handled by build_oauth_installation_form instead")
            # OAuth flows typically don't use this payload structure
            # They use the installation form URL approach

        logger.info(f"Final dynamic payload structure:")
        logger.info(f"- Flow type: {flow_type}")
        logger.info(f"- Service ID: {service_id}")
        logger.info(f"- Mapped fields: {list(auth_data.keys())}")
        logger.info(f"- Required fields satisfied: {[f for f in required_fields if f in auth_data]}")

        return payload


class StatusService:
    """Service for checking integration status"""

    @staticmethod
    async def check_integration_status(
            sub_organization_external_key: str,
            service_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check the status of an integration across all service categories."""
        logger.info(f"Checking integration status for sub_organization_external_key: {sub_organization_external_key}")

        try:
            headers = extract_headers_from_request()
            url = f"{settings.integration_mgr_base_url}/api/v1/integrations/search"

            # Build filter - start with basic filters
            filter_conditions = [
                {
                    "property": "/state",
                    "operator": "=",
                    "values": ["ACTIVE"]
                },
                {
                    "property": "/subOrganization/externalKey",
                    "operator": "=",
                    "values": [sub_organization_external_key]
                }
            ]

            # Add service type filter if provided
            if service_type:
                filter_conditions.append({
                    "property": "/type",
                    "operator": "=",
                    "values": [service_type.upper()]
                })

            payload = {
                "filter": {
                    "and": filter_conditions
                },
                "pagination": {
                    "offset": 0,
                    "limit": 999
                }
            }

            response = await http_client_service.make_request("post", url, headers, json_data=payload)

            # Handle different response formats
            if isinstance(response, dict):
                response_data = response
                integrations = response_data.get("data", [])
            elif isinstance(response, list):
                integrations = response
                response_data = {"data": response}
            else:
                integrations = []
                response_data = {}

            if integrations:
                # Return details of found integrations
                integration_details = []
                for integration in integrations:
                    integration_info = {
                        "id": integration.get("id"),
                        "name": integration.get("name"),
                        "type": integration.get("type"),
                        "connector_name": integration.get("serviceProfile", {}).get("name"),
                        "service_display_name": integration.get("serviceProfile", {}).get("displayName"),
                        "state": integration.get("state"),
                        "created_at": integration.get("createdAt"),
                        "sub_organization": {
                            "name": integration.get("subOrganization", {}).get("name"),
                            "external_key": integration.get("subOrganization", {}).get("externalKey")
                        }
                    }
                    integration_details.append(integration_info)

                return ResponseFormatter.success_response(
                    message=f"Found {len(integrations)} active integration(s) for the provided external key",
                    data={
                        "integrations": integration_details,
                        "search_criteria": {
                            "sub_organization_external_key": sub_organization_external_key,
                            "connector_type": service_type
                        }
                    }
                )
            else:
                return {
                    "status": "not_found",
                    "message": f"No active integrations found for sub_organization_external_key: {sub_organization_external_key}" +
                               (f" with service type: {service_type}" if service_type else ""),
                    "search_criteria": {
                        "sub_organization_external_key": sub_organization_external_key,
                        "connector_type": service_type
                    }
                }

        except Exception as e:
            logger.error(f"Error checking integration status: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to check integration status: {str(e)}",
                error_details=traceback.format_exc()
            )


class ResponseFormatter:
    """Helper class for formatting API responses"""

    @staticmethod
    def success_response(message: str, data: Any = None, **kwargs) -> Dict[str, Any]:
        response = APIResponse(
            status="success",
            message=message,
            data=data,
            **kwargs
        )
        return response.dict()

    @staticmethod
    def error_response(message: str, error_details: Any = None, **kwargs) -> Dict[str, Any]:
        response = APIResponse(
            status="error",
            message=message,
            error_details=error_details,
            **kwargs
        )
        return response.dict()


class PlatformListingService:
    """Service for listing connectors and integrations across all categories"""

    @staticmethod
    async def list_all_available_connectors() -> Dict[str, Any]:
        """Get list of all available connectors across all integration categories"""
        logger.info("Listing all available connectors across all categories")

        try:
            headers = extract_headers_from_request()

            # Build filter - ONLY organization/suborganization filter
            filter_conditions = []

            # Check for suborganizationId first
            suborganization_id = headers.get("suborganizationId")
            organization_id = headers.get("organizationId")

            if suborganization_id:
                # If suborganizationId exists, filter by subOrganization/externalKey
                filter_conditions.append({
                    "property": "/subOrganization/externalKey",
                    "operator": "=",
                    "values": [suborganization_id]
                })
                logger.info(f"Filtering by subOrganization/externalKey: {suborganization_id}")
            elif organization_id:
                # If no suborganizationId, filter by organization/id
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

            # Extract integrations
            integrations = response.get("data", []) if isinstance(response, dict) else []

            # Extract unique connectors (service profiles)
            connectors = []
            seen_connectors = set()

            for integration in integrations:
                service_profile = integration.get("serviceProfile", {})
                connector_name = service_profile.get("name", "").lower()
                connector_type = integration.get("type", "")

                # Create unique key
                connector_key = f"{connector_name}:{connector_type}"

                if connector_key not in seen_connectors and connector_name:
                    seen_connectors.add(connector_key)
                    connectors.append({
                        "name": connector_name,
                        "displayName": service_profile.get("displayName", connector_name),
                        "type": connector_type,
                        "description": service_profile.get("description", ""),
                        "serviceId": service_profile.get("id", ""),
                        "category": connector_type
                    })

            # Sort by type and name
            connectors.sort(key=lambda x: (x["type"], x["name"]))

            # Group by category
            connectors_by_category = {}
            for connector in connectors:
                category = connector["type"]
                if category not in connectors_by_category:
                    connectors_by_category[category] = []
                connectors_by_category[category].append(connector)

            return ResponseFormatter.success_response(
                message=f"Found {len(connectors)} connectors across {len(connectors_by_category)} categories",
                data={
                    "connectors": connectors,
                    "connectorsByCategory": connectors_by_category,
                    "totalCount": len(connectors),
                    "categoryCount": len(connectors_by_category),
                    "categories": list(connectors_by_category.keys())
                }
            )

        except Exception as e:
            logger.error(f"Error listing all available connectors: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to list connectors: {str(e)}",
                error_details=traceback.format_exc()
            )

    @staticmethod
    async def list_all_available_integrations(
            connector: Optional[str] = None,
            category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get list of all integrations across all categories, optionally filtered by connector or category"""
        logger.info(f"Listing all integrations - connector: {connector}, category: {category}")

        try:
            headers = extract_headers_from_request()

            # Build filter conditions
            filter_conditions = []

            # Add organization/suborganization filter
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

            # Add connector filter if provided
            if connector:
                filter_conditions.append({
                    "property": "/serviceProfile/name",
                    "operator": "=",
                    "values": [connector]
                })
                logger.info(f"Filtering by connector: {connector}")

            # Add category filter if provided
            if category:
                filter_conditions.append({
                    "property": "/type",
                    "operator": "=",
                    "values": [category.upper()]
                })
                logger.info(f"Filtering by category: {category}")

            payload = {
                "filter": {
                    "and": filter_conditions
                },
                "pagination": {"offset": 0, "limit": 999}
            }

            url = f"{settings.integration_mgr_base_url}/api/v1/integrations/search"
            response = await http_client_service.make_request("post", url, headers, json_data=payload)

            # Extract integrations
            integrations = response.get("data", []) if isinstance(response, dict) else []

            # Transform integrations for response
            formatted_integrations = []
            integrations_by_category = {}
            integrations_by_connector = {}

            for integration in integrations:
                service_profile = integration.get("serviceProfile", {})
                connector_name = service_profile.get("name", "").lower()
                integration_type = integration.get("type", "")

                formatted_integration = {
                    "id": integration.get("id"),
                    "name": integration.get("name"),
                    "connector": connector_name,
                    "connectorDisplayName": service_profile.get("displayName", connector_name),
                    "type": integration_type,
                    "category": integration_type,
                    "state": integration.get("state"),
                    "createdAt": integration.get("createdAt"),
                    "subOrganization": integration.get("subOrganization", {})
                }

                formatted_integrations.append(formatted_integration)

                # Group by category
                if integration_type not in integrations_by_category:
                    integrations_by_category[integration_type] = []
                integrations_by_category[integration_type].append(formatted_integration)

                # Group by connector
                if connector_name not in integrations_by_connector:
                    integrations_by_connector[connector_name] = []
                integrations_by_connector[connector_name].append(formatted_integration)

            return ResponseFormatter.success_response(
                message=f"Found {len(formatted_integrations)} integrations" +
                        (f" for connector '{connector}'" if connector else "") +
                        (f" in category '{category}'" if category else ""),
                data={
                    "integrations": formatted_integrations,
                    "integrationsByCategory": integrations_by_category,
                    "integrationsByConnector": integrations_by_connector,
                    "totalCount": len(formatted_integrations),
                    "categoryCount": len(integrations_by_category),
                    "connectorCount": len(integrations_by_connector),
                    "categories": list(integrations_by_category.keys()),
                    "connectors": list(integrations_by_connector.keys())
                }
            )

        except Exception as e:
            logger.error(f"Error listing all integrations: {str(e)}")
            return ResponseFormatter.error_response(
                message=f"Failed to list integrations: {str(e)}",
                error_details=traceback.format_exc()
            )