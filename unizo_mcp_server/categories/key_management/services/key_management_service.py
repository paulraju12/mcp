import traceback
import structlog
from typing import Dict, Any, Optional

from .key_management_integration import key_management_integration_service
from ..models.key_management_models import (
    VaultConfigRequest
)

logger = structlog.getLogger(__name__)


class KeyManagementService:
    """Service for managing key management operations"""

    async def list_vault_configs(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List vault configurations with filtering options"""
        logger.info(f"Listing vault configurations for integration: {integration_id}")
        try:
            result = await key_management_integration_service.list_vault_configs(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                configs_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(configs_data)} vault configurations",
                    "data": {
                        "vault_configs": configs_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(configs_data)) if pagination else len(configs_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_vault_configs: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_vault_config_details(
            self,
            integration_id: str,
            vault_config_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific vault configuration"""
        logger.info(f"Getting vault configuration details for config: {vault_config_id}")
        try:
            result = await key_management_integration_service.get_vault_config(
                integration_id=integration_id,
                vault_config_id=vault_config_id
            )

            if result["status"] == "success":
                config_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved vault configuration details for {vault_config_id}",
                    "data": {
                        "vault_config": config_data
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting vault configuration details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_vault_config(
            self,
            integration_id: str,
            name: str
    ) -> Dict[str, Any]:
        """Create a new vault configuration"""
        logger.info(f"Creating vault configuration for integration: {integration_id}")
        try:
            vault_config_request = VaultConfigRequest(
                integrationId=integration_id,
                name=name
            )

            result = await key_management_integration_service.create_vault_config(
                integration_id=integration_id,
                vault_config_request=vault_config_request
            )

            if result["status"] == "success":
                config_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Created vault configuration: {name}",
                    "data": {
                        "vault_config": config_data
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error creating vault configuration: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


# Global key management service instance
key_management_service = KeyManagementService()