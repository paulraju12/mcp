import structlog
from typing import Dict, Any, List, Optional

from .services.incident_integration import incident_integration_service
from .services.incident_management import incident_service
from .models.incident_models import (
    IncidentCreateRequest, IncidentUpdateRequest, Priority, Target, Project, ServiceInfo,
    IncidentStatus, IncidentPriority, PriorityName, IncidentType, TargetType
)
from tempory.core import BaseScopedTools

logger = structlog.getLogger(__name__)


class IncidentTools(BaseScopedTools):
    """MCP tools for Incident Management operations"""

    def __init__(self, mcp_server):
        super().__init__(mcp_server, scope='incident')

    def _register_tools(self):
        """Register all MCP tools for incident management"""
        # Global connector tools
        self.register_tool(name="incident_list_connectors")(self.incident_connectors)
        self.register_tool(name="incident_list_integrations")(self.incident_integrations)

        # Organization tools
        self.register_tool(name="incident_list_organizations")(self.list_organizations)
        self.register_tool(name="incident_get_organization")(self.get_organization)

        # Service tools
        self.register_tool(name="incident_list_services_for_org")(self.list_services)
        self.register_tool(name="incident_get_service")(self.get_service)

        # Team tools
        self.register_tool(name="incident_list_teams")(self.list_teams)
        self.register_tool(name="incident_get_team")(self.get_team)

        # Incident tools
        self.register_tool(name="incident_list_incidents")(self.list_incidents)
        self.register_tool(name="incident_get_incident")(self.get_incident)
        self.register_tool(name="incident_create_incident")(self.create_incident)
        self.register_tool(name="incident_update_incident")(self.update_incident)



    #--------Connector Tools----------
    async def incident_connectors(self) -> List[dict]:
        """Get list of available incident connectors"""
        logger.info("MCP tool: list_connectors called for incident")
        connectors = await incident_integration_service.get_connectors()
        return [connector.dict() if hasattr(connector, 'dict') else connector for connector in connectors]

    async def incident_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific connector"""
        logger.info(f"MCP tool: list_integrations called for incident connector: {connector}")
        integrations = await incident_integration_service.get_integrations(connector)
        return [integration.dict() if hasattr(integration, 'dict') else integration for integration in integrations]

    #---------organization Tools----------

    async def list_organizations(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> List[dict]:
        """Get list of organizations for incident management

        Args:
            integration_id: The integration ID to use for the request
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 20)
            sort: Field to sort by (optional)
        """
        logger.info(f"MCP tool: list_organizations called for integration: {integration_id}")
        organizations = await incident_integration_service.get_organizations(integration_id, offset, limit, sort)
        return [org.dict() for org in organizations]

    async def get_organization(self, integration_id: str, organization_id: str) -> Optional[dict]:
        """Get a specific organization by ID

        Args:
            integration_id: The integration ID to use for the request
            organization_id: The unique identifier of the organization
        """
        logger.info(f"MCP tool: get_organization called for organization: {organization_id}")
        organization = await incident_integration_service.get_organization(integration_id, organization_id)
        return organization.dict() if organization else None

    async def list_services(
            self,
            integration_id: str,
            organization_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> List[dict]:
        """Get list of services for an organization

        Args:
            integration_id: The integration ID to use for the request
            organization_id: The unique identifier of the organization
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 20)
            sort: Field to sort by (optional)
        """
        logger.info(f"MCP tool: list_services called for organization: {organization_id}")
        services = await incident_integration_service.get_services(integration_id, organization_id, offset, limit, sort)
        return [service.dict() for service in services]

    async def get_service(self, integration_id: str, organization_id: str, service_id: str) -> Optional[dict]:
        """Get a specific service by ID

        Args:
            integration_id: The integration ID to use for the request
            organization_id: The unique identifier of the organization
            service_id: The unique identifier of the service
        """
        logger.info(f"MCP tool: get_service called for service: {service_id}")
        service = await incident_integration_service.get_service(integration_id, organization_id, service_id)
        return service.dict() if service else None

    async def list_teams(
            self,
            integration_id: str,
            organization_id: str,
            service_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None
    ) -> List[dict]:
        """Get list of teams for a service

        Args:
            integration_id: The integration ID to use for the request
            organization_id: The unique identifier of the organization
            service_id: The unique identifier of the service
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 20)
            sort: Field to sort by (optional)
        """
        logger.info(f"MCP tool: list_teams called for service: {service_id}")
        teams = await incident_integration_service.get_teams(integration_id, organization_id, service_id, offset, limit,
                                                             sort)
        return [team.dict() for team in teams]

    async def get_team(
            self,
            integration_id: str,
            organization_id: str,
            service_id: str,
            team_id: str
    ) -> Optional[dict]:
        """Get a specific team by ID

        Args:
            integration_id: The integration ID to use for the request
            organization_id: The unique identifier of the organization
            service_id: The unique identifier of the service
            team_id: The unique identifier of the team
        """
        logger.info(f"MCP tool: get_team called for team: {team_id}")
        team = await incident_integration_service.get_team(integration_id, organization_id, service_id, team_id)
        return team.dict() if team else None

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
        """List incidents for a specific team

        Args:
            integration_id: The integration ID to use for the request
            organization_id: The unique identifier of the organization
            service_id: The unique identifier of the service
            team_id: The unique identifier of the team
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 20)
            sort: Field to sort by (optional)
        """
        logger.info(f"MCP tool: list_incidents called for team: {team_id}")
        return await incident_service.list_incidents(
            integration_id, organization_id, service_id, team_id, offset, limit, sort
        )

    async def get_incident(
            self,
            integration_id: str,
            organization_id: str,
            service_id: str,
            team_id: str,
            incident_id: str
    ) -> Dict[str, Any]:
        """Get a specific incident by ID

        Args:
            integration_id: The integration ID to use for the request
            organization_id: The unique identifier of the organization
            service_id: The unique identifier of the service
            team_id: The unique identifier of the team
            incident_id: The unique identifier of the incident
        """
        logger.info(f"MCP tool: get_incident called for incident: {incident_id}")
        return await incident_service.get_incident(
            integration_id, organization_id, service_id, team_id, incident_id
        )

    async def create_incident(
            self,
            integration_id: str,
            organization_id: str,
            service_id: str,
            team_id: str,
            name: str,
            title: str,
            description: str,
            status: str,
            priority_type: str,
            priority_id: str,
            priority_name: str,
            service_type: str,
            service_info_id: str,
            service_name: str,
            username: Optional[str] = None,
            incident_type: Optional[str] = None,
            targets: Optional[List[Dict[str, str]]] = None,
            is_multi_responder: Optional[bool] = None,
            project_type: Optional[str] = None,
            project_id: Optional[str] = None,
            project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new incident

        Args:
            integration_id: The integration ID to use for the request
            organization_id: The unique identifier of the organization
            service_id: The unique identifier of the service
            team_id: The unique identifier of the team
            name: Name of the incident (5-100 characters)
            title: Title of the incident (10-200 characters)
            description: Description of the incident (20-1000 characters)
            status: Current status of the incident (investigating, identified, monitoring, resolved, postmortem)
            priority_type: Priority type (P1, P2, P3, P4)
            priority_id: Unique identifier of the priority
            priority_name: Name of the priority (Critical, High, Medium, Low)
            service_type: Type of the service
            service_info_id: Unique identifier of the service
            service_name: Name of the service
            username: Username of the incident creator (optional)
            incident_type: Type of the incident (service, infrastructure, security, performance) (optional)
            targets: List of affected targets (optional)
            is_multi_responder: Whether multiple responders are assigned (optional)
            project_type: Type of the project (optional)
            project_id: Unique identifier of the project (optional)
            project_name: Name of the project (optional)
        """
        logger.info(f"MCP tool: create_incident called with name: {name}")
        try:
            # Create priority object
            priority = Priority(
                type=IncidentPriority(priority_type),
                id=priority_id,
                name=PriorityName(priority_name)
            )

            # Create service info object
            service_info = ServiceInfo(
                type=service_type,
                id=service_info_id,
                name=service_name
            )

            # Create targets if provided
            target_objects = None
            if targets:
                target_objects = [
                    Target(type=TargetType(target["type"]), slug=target["slug"])
                    for target in targets
                ]

            # Create project if provided
            project = None
            if project_id and project_name:
                project = Project(
                    type=project_type,
                    id=project_id,
                    name=project_name
                )

            # Create incident request
            incident_request = IncidentCreateRequest(
                name=name,
                title=title,
                description=description,
                status=IncidentStatus(status),
                username=username,
                type=IncidentType(incident_type) if incident_type else None,
                targets=target_objects,
                isMultiResponder=is_multi_responder,
                priority=priority,
                project=project,
                service=service_info
            )

            return await incident_service.create_incident(
                integration_id, organization_id, service_id, team_id, incident_request
            )
        except Exception as e:
            logger.error(f"Error creating incident: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create incident: {str(e)}"
            }

    async def update_incident(
            self,
            integration_id: str,
            organization_id: str,
            service_id: str,
            team_id: str,
            incident_id: str,
            name: Optional[str] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
            status: Optional[str] = None,
            username: Optional[str] = None,
            incident_type: Optional[str] = None,
            targets: Optional[List[Dict[str, str]]] = None,
            is_multi_responder: Optional[bool] = None,
            priority_type: Optional[str] = None,
            priority_id: Optional[str] = None,
            priority_name: Optional[str] = None,
            service_type: Optional[str] = None,
            service_info_id: Optional[str] = None,
            service_name: Optional[str] = None,
            project_type: Optional[str] = None,
            project_id: Optional[str] = None,
            project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing incident

        Args:
            integration_id: The integration ID to use for the request
            organization_id: The unique identifier of the organization
            service_id: The unique identifier of the service
            team_id: The unique identifier of the team
            incident_id: The unique identifier of the incident to update
            name: Name of the incident (5-100 characters) (optional)
            title: Title of the incident (10-200 characters) (optional)
            description: Description of the incident (20-1000 characters) (optional)
            status: Current status of the incident (investigating, identified, monitoring, resolved, postmortem) (optional)
            username: Username of the incident creator (optional)
            incident_type: Type of the incident (service, infrastructure, security, performance) (optional)
            targets: List of affected targets (optional)
            is_multi_responder: Whether multiple responders are assigned (optional)
            priority_type: Priority type (P1, P2, P3, P4) (optional)
            priority_id: Unique identifier of the priority (optional)
            priority_name: Name of the priority (Critical, High, Medium, Low) (optional)
            service_type: Type of the service (optional)
            service_info_id: Unique identifier of the service (optional)
            service_name: Name of the service (optional)
            project_type: Type of the project (optional)
            project_id: Unique identifier of the project (optional)
            project_name: Name of the project (optional)
        """
        logger.info(f"MCP tool: update_incident called for incident: {incident_id}")
        try:
            # Create priority object if all priority fields are provided
            priority = None
            if priority_type and priority_id and priority_name:
                priority = Priority(
                    type=IncidentPriority(priority_type),
                    id=priority_id,
                    name=PriorityName(priority_name)
                )

            # Create service info object if all service fields are provided
            service_info = None
            if service_info_id and service_name:
                service_info = ServiceInfo(
                    type=service_type,
                    id=service_info_id,
                    name=service_name
                )

            # Create targets if provided
            target_objects = None
            if targets:
                target_objects = [
                    Target(type=TargetType(target["type"]), slug=target["slug"])
                    for target in targets
                ]

            # Create project if provided
            project = None
            if project_id and project_name:
                project = Project(
                    type=project_type,
                    id=project_id,
                    name=project_name
                )

            # Create incident update request
            incident_request = IncidentUpdateRequest(
                name=name,
                title=title,
                description=description,
                status=IncidentStatus(status) if status else None,
                username=username,
                type=IncidentType(incident_type) if incident_type else None,
                targets=target_objects,
                isMultiResponder=is_multi_responder,
                priority=priority,
                project=project,
                service=service_info
            )

            return await incident_service.update_incident(
                integration_id, organization_id, service_id, team_id, incident_id, incident_request
            )
        except Exception as e:
            logger.error(f"Error updating incident: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to update incident: {str(e)}"
            }