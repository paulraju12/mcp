import traceback
import structlog
from typing import Dict, Any, Optional

from .pcr_integration import pcr_integration_service

logger = structlog.getLogger(__name__)


class PCRService:
    """Service for managing PCR operations"""

    # ---------- ORGANIZATION METHODS ----------
    async def list_organizations(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20
    ) -> Dict[str, Any]:
        """List organizations"""
        logger.info(f"Listing organizations for integration: {integration_id}")
        try:
            result = await pcr_integration_service.list_organizations(
                integration_id=integration_id,
                offset=offset,
                limit=limit
            )

            if result["status"] == "success":
                organizations_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(organizations_data)} organizations",
                    "data": {
                        "organizations": organizations_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(organizations_data)) if pagination else len(organizations_data)
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
            result = await pcr_integration_service.get_organization(
                integration_id=integration_id,
                organization_id=organization_id
            )

            if result["status"] == "success":
                organization_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved organization details for {organization_id}",
                    "data": {
                        "organization": organization_data
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

    # ---------- REPOSITORY METHODS ----------
    async def list_repositories(
            self,
            integration_id: str,
            organization_id: str,
            offset: int = 0,
            limit: int = 20
    ) -> Dict[str, Any]:
        """List repositories for an organization"""
        logger.info(f"Listing repositories for organization: {organization_id}")
        try:
            result = await pcr_integration_service.list_repositories(
                integration_id=integration_id,
                organization_id=organization_id,
                offset=offset,
                limit=limit
            )

            if result["status"] == "success":
                repositories_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(repositories_data)} repositories for organization {organization_id}",
                    "data": {
                        "repositories": repositories_data,
                        "pagination": pagination,
                        "organization_id": organization_id,
                        "total_count": pagination.get("total", len(repositories_data)) if pagination else len(repositories_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_repositories: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_repository_details(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific repository"""
        logger.info(f"Getting repository details for repository: {repository_id}")
        try:
            result = await pcr_integration_service.get_repository(
                integration_id=integration_id,
                organization_id=organization_id,
                repository_id=repository_id
            )

            if result["status"] == "success":
                repository_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved repository details for {repository_id}",
                    "data": {
                        "repository": repository_data,
                        "organization_id": organization_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting repository details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # ---------- ARTIFACT METHODS ----------
    async def list_artifacts(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List artifacts for a repository"""
        logger.info(f"Listing artifacts for repository: {repository_id}")
        try:
            result = await pcr_integration_service.list_artifacts(
                integration_id=integration_id,
                organization_id=organization_id,
                repository_id=repository_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                artifacts_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(artifacts_data)} artifacts for repository {repository_id}",
                    "data": {
                        "artifacts": artifacts_data,
                        "pagination": pagination,
                        "organization_id": organization_id,
                        "repository_id": repository_id,
                        "total_count": pagination.get("total", len(artifacts_data)) if pagination else len(artifacts_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error listing artifacts: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_artifact_details(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str,
            artifact_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific artifact"""
        logger.info(f"Getting artifact details for artifact: {artifact_id}")
        try:
            result = await pcr_integration_service.get_artifact(
                integration_id=integration_id,
                organization_id=organization_id,
                repository_id=repository_id,
                artifact_id=artifact_id
            )

            if result["status"] == "success":
                artifact_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved artifact details for {artifact_id}",
                    "data": {
                        "artifact": artifact_data,
                        "organization_id": organization_id,
                        "repository_id": repository_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting artifact details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # ---------- TAG METHODS ----------
    async def list_tags(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str,
            artifact_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List tags for an artifact"""
        logger.info(f"Listing tags for artifact: {artifact_id}")
        try:
            result = await pcr_integration_service.list_tags(
                integration_id=integration_id,
                organization_id=organization_id,
                repository_id=repository_id,
                artifact_id=artifact_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                tags_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(tags_data)} tags for artifact {artifact_id}",
                    "data": {
                        "tags": tags_data,
                        "pagination": pagination,
                        "organization_id": organization_id,
                        "repository_id": repository_id,
                        "artifact_id": artifact_id,
                        "total_count": pagination.get("total", len(tags_data)) if pagination else len(tags_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error listing tags: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_tag_details(
            self,
            integration_id: str,
            organization_id: str,
            repository_id: str,
            artifact_id: str,
            tag_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific tag"""
        logger.info(f"Getting tag details for tag: {tag_id}")
        try:
            result = await pcr_integration_service.get_tag(
                integration_id=integration_id,
                organization_id=organization_id,
                repository_id=repository_id,
                artifact_id=artifact_id,
                tag_id=tag_id
            )

            if result["status"] == "success":
                tag_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved tag details for {tag_id}",
                    "data": {
                        "tag": tag_data,
                        "organization_id": organization_id,
                        "repository_id": repository_id,
                        "artifact_id": artifact_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting tag details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


# Global PCR service instance
pcr_service = PCRService()