import traceback
import structlog
from typing import Dict, Any, Optional

from .edr_integration import edr_integration_service

logger = structlog.getLogger(__name__)


class EDRService:
    """Service for managing EDR operations"""

    async def list_devices(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List devices with pagination and sorting"""
        logger.info(f"Listing devices for integration: {integration_id}")
        try:
            result = await edr_integration_service.list_devices(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                devices_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(devices_data)} devices",
                    "data": {
                        "devices": devices_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(devices_data)) if pagination else len(devices_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_devices: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_device_details(
            self,
            integration_id: str,
            device_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific device"""
        logger.info(f"Getting device details for device: {device_id}")
        try:
            result = await edr_integration_service.get_device(
                integration_id=integration_id,
                device_id=device_id
            )

            if result["status"] == "success":
                device_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved device details for {device_id}",
                    "data": {
                        "device": device_data
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting device details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def list_device_alerts(
            self,
            integration_id: str,
            device_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List alerts for a specific device"""
        logger.info(f"Listing alerts for device: {device_id}")
        try:
            result = await edr_integration_service.list_device_alerts(
                integration_id=integration_id,
                device_id=device_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                alerts_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(alerts_data)} alerts for device {device_id}",
                    "data": {
                        "alerts": alerts_data,
                        "pagination": pagination,
                        "device_id": device_id,
                        "total_count": pagination.get("total", len(alerts_data)) if pagination else len(alerts_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error listing device alerts: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_device_alert_details(
            self,
            integration_id: str,
            device_id: str,
            alert_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific device alert"""
        logger.info(f"Getting alert details for alert: {alert_id} on device: {device_id}")
        try:
            result = await edr_integration_service.get_device_alert(
                integration_id=integration_id,
                device_id=device_id,
                alert_id=alert_id
            )

            if result["status"] == "success":
                alert_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved alert details for {alert_id}",
                    "data": {
                        "alert": alert_data,
                        "device_id": device_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting device alert details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


# Global EDR service instance
edr_service = EDRService()