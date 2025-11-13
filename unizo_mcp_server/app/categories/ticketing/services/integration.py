import structlog
import traceback
from typing import List, Dict, Any
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request
from ..models.ticket_models import (
    Organization, Collection, CollectionCreateRequest, CollectionStatistics,
    User, ChangeLog
)

logger = structlog.getLogger(__name__)


class IntegrationService:
    async def get_connectors(self) -> List[dict]:
        """Get list of available TICKETING connectors"""
        logger.info("Getting list of TICKETING connectors")
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
            response: Dict[str, Any] = await http_client_service.make_request("post", url, headers, json_data=payload)
            integrations = response.get("data", [])

            logger.info(f"Retrieved {len(integrations)} total integrations from API")

            # Filter for TICKETING type in code
            connectors = []
            seen_connectors = set()
            for integ in integrations:
                # Check if it's a TICKETING integration
                if integ.get("type") == "TICKETING" and "serviceProfile" in integ and "name" in integ["serviceProfile"]:
                    connector_name = integ["serviceProfile"]["name"].lower()
                    if connector_name not in seen_connectors:
                        connectors.append({"name": connector_name})
                        seen_connectors.add(connector_name)

            logger.info(f"Found {len(connectors)} TICKETING connectors after filtering")
            return connectors
        except Exception as e:
            logger.error(f"Error getting TICKETING connectors: {str(e)}")
            return []

    async def get_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific TICKETING connector"""
        logger.info(f"Getting TICKETING integrations for connector: {connector}")
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
            integrations = response.get("data", [])

            logger.info(f"Retrieved {len(integrations)} total integrations from API")

            # Filter for TICKETING type and matching connector name in code
            matching_integrations = [
                {"id": integ.get("id"), "name": integ.get("name", "Unnamed Integration")}
                for integ in integrations
                if integ.get("type") == "TICKETING" and
                   "serviceProfile" in integ and
                   "name" in integ["serviceProfile"] and
                   integ["serviceProfile"]["name"].lower() == connector.lower()
            ]

            logger.info(f"Found {len(matching_integrations)} integrations for TICKETING connector {connector} after filtering")
            return matching_integrations
        except Exception as e:
            logger.error(f"Error getting TICKETING integrations: {str(e)}")
            return []

    async def get_organizations(self, integration_id: str) -> List[Organization]:
        """Get organizations for an integration"""
        logger.info(f"Getting organizations for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            # Check if it's a Jira integration
            url = f"{settings.integration_mgr_base_url}/api/v1/integrations/{integration_id}"
            response = await http_client_service.make_request("get", url, headers)
            integration_data = response

            is_jira = (
                    "serviceProfile" in integration_data and
                    "name" in integration_data["serviceProfile"] and
                    integration_data["serviceProfile"]["name"].lower() == "jira"
            )

            if is_jira:
                logger.info("Detected Jira integration, returning default organization")
                return [Organization(id="default", name="Default Organization")]

            # Get organizations from ticketing API
            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/organizations"
            response = await http_client_service.make_request("get", url, headers)
            organizations = response.get("data", [])

            result = [
                Organization(
                    id=org["id"],
                    name=org.get("name", org["id"]),
                    description=org.get("description"),
                    login=org.get("login"),
                    target_url=org.get("targetUrl"),
                    avatar_url=org.get("avatarUrl"),
                    change_log=ChangeLog(**org.get("changeLog", {})) if org.get("changeLog") else None
                )
                for org in organizations
            ]

            logger.info(f"Found {len(result)} organizations")
            return result
        except Exception as e:
            logger.error(f"Error getting organizations: {str(e)}")
            return []

    async def get_organization(self, integration_id: str, organization_id: str) -> Dict[str, Any]:
        """Get a specific organization by ID"""
        logger.info(f"Getting organization: {organization_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/organizations/{organization_id}"
            response = await http_client_service.make_request("get", url, headers)

            org = response
            organization = Organization(
                id=org["id"],
                name=org.get("name", org["id"]),
                description=org.get("description"),
                login=org.get("login"),
                target_url=org.get("targetUrl"),
                avatar_url=org.get("avatarUrl"),
                change_log=ChangeLog(**org.get("changeLog", {})) if org.get("changeLog") else None
            )

            result = {
                "status": "success",
                "message": "Organization retrieved successfully",
                "organization": organization.dict()
            }

            logger.info(f"Organization retrieved successfully: {organization_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting organization: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_collections(self, integration_id: str, organization_id: str) -> List[Collection]:
        """Get collections for an organization"""
        logger.info(f"Getting collections for integration: {integration_id}, org: {organization_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections"
            response = await http_client_service.make_request("get", url, headers)
            collections = response.get("data", [])

            result = []
            for coll in collections:
                collection_data = {
                    "id": coll.get("id"),
                    "name": coll.get("name", "Unnamed Collection"),
                    "type": coll.get("type", "Project")
                }

                # Add optional fields if they exist
                optional_fields = [
                    "description", "key", "owner", "access_level", "target_url",
                    "status", "start_date", "end_date", "metadata"
                ]

                for field in optional_fields:
                    api_field = field
                    if field == "access_level":
                        api_field = "accessLevel"
                    elif field == "target_url":
                        api_field = "targetUrl"
                    elif field == "start_date":
                        api_field = "startDate"
                    elif field == "end_date":
                        api_field = "endDate"

                    if api_field in coll:
                        collection_data[field] = coll[api_field]

                # Handle members (list of users)
                if "members" in coll and isinstance(coll["members"], list):
                    collection_data["members"] = [
                        User(
                            id=member.get("id", "unknown"),
                            href=member.get("href"),
                            first_name=member.get("firstName"),
                            last_name=member.get("lastName"),
                            avatar=member.get("avatar")
                        )
                        for member in coll["members"]
                    ]

                # Handle statistics
                if "statistics" in coll and isinstance(coll["statistics"], dict):
                    stats = coll["statistics"]
                    collection_data["statistics"] = CollectionStatistics(
                        total_tickets=stats.get("totalTickets"),
                        open_tickets=stats.get("openTickets"),
                        completed_tickets=stats.get("completedTickets"),
                        progress=stats.get("progress")
                    )

                # Handle change log
                if "changeLog" in coll and isinstance(coll["changeLog"], dict):
                    collection_data["change_log"] = ChangeLog(**coll["changeLog"])

                result.append(Collection(**collection_data))

            logger.info(f"Found {len(result)} collections")
            return result
        except Exception as e:
            logger.error(f"Error getting collections: {str(e)}")
            return []

    async def get_collection(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str
    ) -> Dict[str, Any]:
        """Get a specific collection by ID"""
        logger.info(f"Getting collection: {collection_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationid"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}"
            response = await http_client_service.make_request("get", url, headers)

            # Build collection data similar to get_collections but for single item
            coll = response
            collection_data = {
                "id": coll.get("id"),
                "name": coll.get("name", "Unnamed Collection"),
                "type": coll.get("type", "Project")
            }

            # Add optional fields
            optional_fields = [
                "description", "key", "owner", "access_level", "target_url",
                "status", "start_date", "end_date", "metadata"
            ]

            for field in optional_fields:
                api_field = field
                if field == "access_level":
                    api_field = "accessLevel"
                elif field == "target_url":
                    api_field = "targetUrl"
                elif field == "start_date":
                    api_field = "startDate"
                elif field == "end_date":
                    api_field = "endDate"

                if api_field in coll:
                    collection_data[field] = coll[api_field]

            # Handle members
            if "members" in coll and isinstance(coll["members"], list):
                collection_data["members"] = [
                    User(
                        id=member.get("id", "unknown"),
                        href=member.get("href"),
                        first_name=member.get("firstName"),
                        last_name=member.get("lastName"),
                        avatar=member.get("avatar")
                    )
                    for member in coll["members"]
                ]

            # Handle statistics
            if "statistics" in coll and isinstance(coll["statistics"], dict):
                stats = coll["statistics"]
                collection_data["statistics"] = CollectionStatistics(
                    total_tickets=stats.get("totalTickets"),
                    open_tickets=stats.get("openTickets"),
                    completed_tickets=stats.get("completedTickets"),
                    progress=stats.get("progress")
                )

            # Handle change log
            if "changeLog" in coll and isinstance(coll["changeLog"], dict):
                collection_data["change_log"] = ChangeLog(**coll["changeLog"])

            collection = Collection(**collection_data)

            result = {
                "status": "success",
                "message": "Collection retrieved successfully",
                "collection": collection.dict()
            }

            logger.info(f"Collection retrieved successfully: {collection_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting collection: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_collection(
            self,
            integration_id: str,
            organization_id: str,
            collection_request: CollectionCreateRequest
    ) -> Dict[str, Any]:
        """Create a new collection"""
        logger.info(f"Creating collection: {collection_request.name}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections"
            response = await http_client_service.make_request(
                "post", url, headers, json_data=collection_request.dict(exclude_none=True)
            )

            result = {
                "status": "success",
                "message": "Collection created successfully",
                "collection": response
            }

            logger.info(f"Collection created successfully")
            return result
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


# Global integration service instance
integration_service = IntegrationService()