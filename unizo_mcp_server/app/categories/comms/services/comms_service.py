import traceback
import structlog
from typing import Dict, Any, Optional, List

from .comms_integration import comms_integration_service
from ..models.comms_models import (
    MessageRequest
)

logger = structlog.getLogger(__name__)


class CommsService:
    """Service for managing communications operations"""

    async def list_organizations(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List organizations with pagination and sorting"""
        logger.info(f"Listing organizations for integration: {integration_id}")
        try:
            result = await comms_integration_service.list_organizations(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                orgs_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(orgs_data)} organizations",
                    "data": {
                        "organizations": orgs_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(orgs_data)) if pagination else len(orgs_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_organizations: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_organization_details(
            self,
            integration_id: str,
            organization_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific organization"""
        logger.info(f"Getting organization details for organization: {organization_id}")
        try:
            result = await comms_integration_service.get_organization(
                integration_id=integration_id,
                organization_id=organization_id
            )

            if result["status"] == "success":
                org_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved organization details for {organization_id}",
                    "data": {
                        "organization": org_data
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting organization details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def list_channels(
            self,
            integration_id: str,
            organization_id: str,
            parent_id: Optional[str] = None,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List channels for an organization with filtering options"""
        logger.info(f"Listing channels for organization: {organization_id}")
        try:
            result = await comms_integration_service.list_channels(
                integration_id=integration_id,
                organization_id=organization_id,
                parent_id=parent_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                channels_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(channels_data)} channels for organization {organization_id}",
                    "data": {
                        "channels": channels_data,
                        "pagination": pagination,
                        "organization_id": organization_id,
                        "parent_id": parent_id,
                        "total_count": pagination.get("total", len(channels_data)) if pagination else len(channels_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error listing channels: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_channel_details(
            self,
            integration_id: str,
            organization_id: str,
            channel_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific channel"""
        logger.info(f"Getting channel details for channel: {channel_id}")
        try:
            result = await comms_integration_service.get_channel(
                integration_id=integration_id,
                organization_id=organization_id,
                channel_id=channel_id
            )

            if result["status"] == "success":
                channel_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved channel details for {channel_id}",
                    "data": {
                        "channel": channel_data,
                        "organization_id": organization_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting channel details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_message(
            self,
            integration_id: str,
            organization_id: str,
            channel_id: str,
            name: Optional[str] = None,
            message_body: str = "",
            attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create a new message in a channel"""
        logger.info(f"Creating message in channel: {channel_id}")
        try:
            # Create message request model
            message_request = MessageRequest(
                name=name,
                messageBody=message_body,
                attachments=attachments
            )

            result = await comms_integration_service.create_message(
                integration_id=integration_id,
                organization_id=organization_id,
                channel_id=channel_id,
                message_data=message_request
            )

            if result["status"] == "success":
                message_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Message created successfully in channel {channel_id}",
                    "data": {
                        "message": message_data,
                        "organization_id": organization_id,
                        "channel_id": channel_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


# Global communications service instance
comms_service = CommsService()