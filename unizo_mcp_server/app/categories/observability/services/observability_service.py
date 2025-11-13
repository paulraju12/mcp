import traceback
import structlog
from typing import Dict, Any, Optional

from .observability_integration import observability_integration_service

logger = structlog.getLogger(__name__)


class ObservabilityService:
    """Service for managing observability operations"""

    async def list_logs(
            self,
            integration_id: str,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List logs with filtering and pagination options"""
        logger.info(f"Listing logs for integration: {integration_id}")
        try:
            result = await observability_integration_service.list_logs(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                logs_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(logs_data)} logs",
                    "data": {
                        "logs": logs_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(logs_data)) if pagination else len(logs_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_logs: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_log_details(
            self,
            integration_id: str,
            log_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific log entry"""
        logger.info(f"Getting log details for log: {log_id}")
        try:
            result = await observability_integration_service.get_log(
                integration_id=integration_id,
                log_id=log_id
            )

            if result["status"] == "success":
                log_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved log details for {log_id}",
                    "data": {
                        "log": log_data
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting log details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


# Global observability service instance
observability_service = ObservabilityService()