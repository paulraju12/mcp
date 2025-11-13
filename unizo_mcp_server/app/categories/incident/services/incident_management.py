import traceback
import structlog
from typing import Dict, Any, Optional

from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request
from ..models.incident_models import (
    Incident, IncidentCreateRequest, IncidentUpdateRequest,
    Priority, Target, Project, ServiceInfo, Team, Organization, Service, ChangeLog
)

logger = structlog.getLogger(__name__)


class IncidentService:

    async def list_incidents(
            self,
            integration_id: str,
            organization_id: str,
            service_id: str,
            team_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List incidents for a specific team"""
        logger.info(f"Listing incidents for team {team_id}, service {service_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }
            if sort:
                params["sort"] = sort

            url = f"{settings.incident_api_base_url}/api/v1/incident/{organization_id}/services/{service_id}/teams/{team_id}/incidents"
            response = await http_client_service.make_request("get", url, headers, params=params)

            incidents_data = response.get("data", [])
            incidents = []

            for incident_data in incidents_data:
                incident = self._parse_incident_data(incident_data)
                incidents.append(incident)

            result = {
                "status": "success",
                "message": f"Found {len(incidents)} incidents",
                "incidents": [incident.dict() for incident in incidents],
                "pagination": response.get("pagination", {}),
                "context": {
                    "integration_id": integration_id,
                    "organization_id": organization_id,
                    "service_id": service_id,
                    "team_id": team_id
                }
            }

            logger.info(f"Successfully retrieved {len(incidents)} incidents")
            return result

        except Exception as e:
            logger.error(f"Error listing incidents: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_incident(
            self,
            integration_id: str,
            organization_id: str,
            service_id: str,
            team_id: str,
            incident_id: str
    ) -> Dict[str, Any]:
        """Get a specific incident by ID"""
        logger.info(f"Getting incident {incident_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.incident_api_base_url}/api/v1/incident/{organization_id}/services/{service_id}/teams/{team_id}/incidents/{incident_id}"
            response = await http_client_service.make_request("get", url, headers)

            if response:
                incident = self._parse_incident_data(response)

                result = {
                    "status": "success",
                    "message": "Incident retrieved successfully",
                    "incident": incident.dict(),
                    "context": {
                        "integration_id": integration_id,
                        "organization_id": organization_id,
                        "service_id": service_id,
                        "team_id": team_id
                    }
                }

                logger.info(f"Successfully retrieved incident {incident_id}")
                return result
            else:
                return {
                    "status": "error",
                    "message": f"Incident {incident_id} not found"
                }

        except Exception as e:
            logger.error(f"Error getting incident {incident_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_incident(
            self,
            integration_id: str,
            organization_id: str,
            service_id: str,
            team_id: str,
            incident_request: IncidentCreateRequest
    ) -> Dict[str, Any]:
        """Create a new incident"""
        logger.info(f"Creating incident: {incident_request.name}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.incident_api_base_url}/api/v1/incident/{organization_id}/services/{service_id}/teams/{team_id}/incidents"
            response = await http_client_service.make_request(
                "post", url, headers, json_data=incident_request.dict(exclude_none=True)
            )

            if response:
                incident = self._parse_incident_data(response)

                result = {
                    "status": "success",
                    "message": f"Incident created successfully with ID: {incident.id}",
                    "incident": incident.dict(),
                    "context": {
                        "integration_id": integration_id,
                        "organization_id": organization_id,
                        "service_id": service_id,
                        "team_id": team_id
                    }
                }

                logger.info(f"Incident created successfully: {incident.id}")
                return result
            else:
                return {
                    "status": "error",
                    "message": "Failed to create incident - no response received"
                }

        except Exception as e:
            logger.error(f"Error creating incident: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def update_incident(
            self,
            integration_id: str,
            organization_id: str,
            service_id: str,
            team_id: str,
            incident_id: str,
            incident_request: IncidentUpdateRequest
    ) -> Dict[str, Any]:
        """Update an existing incident"""
        logger.info(f"Updating incident {incident_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.incident_api_base_url}/api/v1/incident/{organization_id}/services/{service_id}/teams/{team_id}/incidents/{incident_id}"
            response = await http_client_service.make_request(
                "put", url, headers, json_data=incident_request.dict(exclude_none=True)
            )

            if response:
                incident = self._parse_incident_data(response)

                result = {
                    "status": "success",
                    "message": "Incident updated successfully",
                    "incident": incident.dict(),
                    "context": {
                        "integration_id": integration_id,
                        "organization_id": organization_id,
                        "service_id": service_id,
                        "team_id": team_id
                    }
                }

                logger.info(f"Incident updated successfully: {incident_id}")
                return result
            else:
                return {
                    "status": "error",
                    "message": "Failed to update incident - no response received"
                }

        except Exception as e:
            logger.error(f"Error updating incident: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    def _parse_incident_data(self, incident_data: Dict[str, Any]) -> Incident:
        """Parse incident data from API response"""
        # Parse priority
        priority = None
        if "priority" in incident_data and incident_data["priority"]:
            priority_data = incident_data["priority"]
            priority = Priority(
                type=priority_data["type"],
                id=priority_data["id"],
                name=priority_data["name"]
            )

        # Parse targets
        targets = None
        if "targets" in incident_data and incident_data["targets"]:
            targets = [
                Target(type=target["type"], slug=target["slug"])
                for target in incident_data["targets"]
            ]

        # Parse project
        project = None
        if "project" in incident_data and incident_data["project"]:
            project_data = incident_data["project"]
            project = Project(
                type=project_data.get("type"),
                id=project_data["id"],
                name=project_data["name"]
            )

        # Parse service
        service = None
        if "service" in incident_data and incident_data["service"]:
            service_data = incident_data["service"]
            service = ServiceInfo(
                type=service_data.get("type"),
                id=service_data["id"],
                name=service_data["name"]
            )

        # Parse team
        team = None
        if "team" in incident_data and incident_data["team"]:
            team_data = incident_data["team"]
            team = Team(
                id=team_data["id"],
                name=team_data["name"],
                href=team_data.get("href"),
                type=team_data.get("type")
            )

        # Parse services list
        services = None
        if "services" in incident_data and incident_data["services"]:
            services = []
            for service_data in incident_data["services"]:
                srv = Service(
                    id=service_data["id"],
                    name=service_data["name"],
                    href=service_data.get("href"),
                    type=service_data.get("type")
                )
                services.append(srv)

        # Parse organization
        organization = None
        if "organization" in incident_data and incident_data["organization"]:
            org_data = incident_data["organization"]
            organization = Organization(
                id=org_data["id"],
                name=org_data["name"],
                login=org_data.get("login")
            )

        # Parse changelog
        change_log = None
        if "changeLog" in incident_data and incident_data["changeLog"]:
            change_log_data = incident_data["changeLog"]
            change_log = ChangeLog(
                createdDateTime=change_log_data.get("createdDateTime"),
                lastUpdatedDateTime=change_log_data.get("lastUpdatedDateTime")
            )

        return Incident(
            id=incident_data["id"],
            name=incident_data["name"],
            title=incident_data.get("title"),
            login=incident_data.get("login"),
            status=incident_data["status"],
            priority=priority,
            description=incident_data.get("description"),
            incidentKey=incident_data.get("incidentKey"),
            createdBy=incident_data.get("createdBy"),
            url=incident_data.get("url"),
            urgency=incident_data.get("urgency"),
            username=incident_data.get("username"),
            targets=targets,
            project=project,
            service=service,
            isMultiResponder=incident_data.get("isMultiResponder"),
            team=team,
            services=services,
            organization=organization,
            changeLog=change_log
        )


# Global incident service instance
incident_service = IncidentService()