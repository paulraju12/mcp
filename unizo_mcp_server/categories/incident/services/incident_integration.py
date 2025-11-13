import structlog
from typing import List, Dict, Any, Optional
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request
from ..models.incident_models import (
    Organization, Service, Team
)

logger = structlog.getLogger(__name__)


class IncidentIntegrationService:

    async def get_connectors(self) -> List[dict]:
        """Get list of available INCIDENT connectors"""
        logger.info("Getting list of INCIDENT connectors")
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

            # Filter for INCIDENT type in code
            connectors = []
            seen_connectors = set()
            for integ in integrations:
                # Check if it's a INCIDENT integration
                if integ.get("type") == "INCIDENT" and "serviceProfile" in integ and "name" in integ["serviceProfile"]:
                    connector_name = integ["serviceProfile"]["name"].lower()
                    if connector_name not in seen_connectors:
                        connectors.append({"name": connector_name})
                        seen_connectors.add(connector_name)

            logger.info(f"Found {len(connectors)} INCIDENT connectors after filtering")
            return connectors
        except Exception as e:
            logger.error(f"Error getting INCIDENT connectors: {str(e)}")
            return []

    async def get_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific INCIDENT connector"""
        logger.info(f"Getting INCIDENT integrations for connector: {connector}")
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

            # Filter for INCIDENT type and matching connector name in code
            matching_integrations = [
                {"id": integ.get("id"), "name": integ.get("name", "Unnamed Integration")}
                for integ in integrations
                if integ.get("type") == "INCIDENT" and
                   "serviceProfile" in integ and
                   "name" in integ["serviceProfile"] and
                   integ["serviceProfile"]["name"].lower() == connector.lower()
            ]

            logger.info(f"Found {len(matching_integrations)} integrations for INCIDENT connector {connector} after filtering")
            return matching_integrations
        except Exception as e:
            logger.error(f"Error getting INCIDENT integrations: {str(e)}")
            return []

    async def get_organizations(self, integration_id: str, offset: int = 0, limit: int = 20,
                                sort: Optional[str] = None) -> List[Organization]:
        """Get list of organizations for incident management"""
        logger.info(f"Getting organizations for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }
            if sort:
                params["sort"] = sort

            url = f"{settings.incident_api_base_url}/api/v1/incident/organizations"
            response: Dict[str, Any] = await http_client_service.make_request(
                "get", url, headers, params=params
            )

            organizations_data = response.get("data", [])
            organizations = []

            for org_data in organizations_data:
                org = Organization(
                    id=org_data["id"],
                    name=org_data["name"],
                    login=org_data.get("login"),
                    changeLog=org_data.get("changeLog")
                )
                organizations.append(org)

            logger.info(f"Found {len(organizations)} organizations")
            return organizations

        except Exception as e:
            logger.error(f"Error getting organizations: {str(e)}")
            return []

    async def get_organization(self, integration_id: str, organization_id: str) -> Optional[Organization]:
        """Get a specific organization by ID"""
        logger.info(f"Getting organization {organization_id} for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.incident_api_base_url}/api/v1/incident/organizations/{organization_id}"
            response = await http_client_service.make_request("get", url, headers)

            if response:
                return Organization(
                    id=response["id"],
                    name=response["name"],
                    login=response.get("login"),
                    changeLog=response.get("changeLog")
                )

            return None

        except Exception as e:
            logger.error(f"Error getting organization {organization_id}: {str(e)}")
            return None

    async def get_services(
            self,
            integration_id: str,
            organization_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> List[Service]:
        """Get list of services for an organization"""
        logger.info(f"Getting services for organization {organization_id}, integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }
            if sort:
                params["sort"] = sort

            url = f"{settings.incident_api_base_url}/api/v1/incident/{organization_id}/services"
            response = await http_client_service.make_request("get", url, headers, params=params)

            services_data = response.get("data", [])
            services = []

            for service_data in services_data:
                # Create team object if present
                team = None
                if "team" in service_data and service_data["team"]:
                    team_data = service_data["team"]
                    team = Team(
                        id=team_data["id"],
                        name=team_data["name"],
                        href=team_data.get("href"),
                        type=team_data.get("type")
                    )

                service = Service(
                    id=service_data["id"],
                    name=service_data["name"],
                    description=service_data.get("description"),
                    team=team,
                    url=service_data.get("url"),
                    href=service_data.get("href"),
                    type=service_data.get("type"),
                    changeLog=service_data.get("changeLog")
                )
                services.append(service)

            logger.info(f"Found {len(services)} services")
            return services

        except Exception as e:
            logger.error(f"Error getting services: {str(e)}")
            return []

    async def get_service(
            self,
            integration_id: str,
            organization_id: str,
            service_id: str
    ) -> Optional[Service]:
        """Get a specific service by ID"""
        logger.info(f"Getting service {service_id} for organization {organization_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.incident_api_base_url}/api/v1/incident/{organization_id}/services/{service_id}"
            response = await http_client_service.make_request("get", url, headers)

            if response:
                # Create team object if present
                team = None
                if "team" in response and response["team"]:
                    team_data = response["team"]
                    team = Team(
                        id=team_data["id"],
                        name=team_data["name"],
                        href=team_data.get("href"),
                        type=team_data.get("type")
                    )

                return Service(
                    id=response["id"],
                    name=response["name"],
                    description=response.get("description"),
                    team=team,
                    url=response.get("url"),
                    href=response.get("href"),
                    type=response.get("type"),
                    changeLog=response.get("changeLog")
                )

            return None

        except Exception as e:
            logger.error(f"Error getting service {service_id}: {str(e)}")
            return None

    async def get_teams(
            self,
            integration_id: str,
            organization_id: str,
            service_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> List[Team]:
        """Get list of teams for a service"""
        logger.info(f"Getting teams for service {service_id}, organization {organization_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            params = {
                "offset": offset,
                "limit": limit
            }
            if sort:
                params["sort"] = sort

            url = f"{settings.incident_api_base_url}/api/v1/incident/{organization_id}/services/{service_id}/teams"
            response = await http_client_service.make_request("get", url, headers, params=params)

            teams_data = response.get("data", [])
            teams = []

            for team_data in teams_data:
                team = Team(
                    id=team_data["id"],
                    name=team_data["name"],
                    description=team_data.get("description"),
                    url=team_data.get("url"),
                    href=team_data.get("href"),
                    type=team_data.get("type"),
                    changeLog=team_data.get("changeLog")
                )
                teams.append(team)

            logger.info(f"Found {len(teams)} teams")
            return teams

        except Exception as e:
            logger.error(f"Error getting teams: {str(e)}")
            return []

    async def get_team(
            self,
            integration_id: str,
            organization_id: str,
            service_id: str,
            team_id: str
    ) -> Optional[Team]:
        """Get a specific team by ID"""
        logger.info(f"Getting team {team_id} for service {service_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.incident_api_base_url}/api/v1/incident/{organization_id}/services/{service_id}/teams/{team_id}"
            response = await http_client_service.make_request("get", url, headers)

            if response:
                return Team(
                    id=response["id"],
                    name=response["name"],
                    description=response.get("description"),
                    url=response.get("url"),
                    href=response.get("href"),
                    type=response.get("type"),
                    changeLog=response.get("changeLog")
                )

            return None

        except Exception as e:
            logger.error(f"Error getting team {team_id}: {str(e)}")
            return None


# Global incident integration service instance
incident_integration_service = IncidentIntegrationService()