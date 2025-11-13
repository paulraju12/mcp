from fastapi import APIRouter, Query, Path, HTTPException, Depends
from typing import Optional, List
import structlog

from .services.incident_integration import incident_integration_service
from .services.incident_management import incident_service
from .models.incident_models import (
    OrganizationsResponse, Organization, ServicesResponse, Service,
    TeamsResponse, Team, IncidentsResponse, Incident,
    IncidentCreateRequest, IncidentUpdateRequest
)

logger = structlog.getLogger(__name__)
router = APIRouter()


# Organization endpoints
@router.get("/incident/organizations", response_model=OrganizationsResponse, tags=["Organization"])
async def list_organizations(
        integration_id: str = Query(..., description="Integration ID"),
        offset: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
        sort: Optional[str] = Query(None, description="Field to sort by")
):
    """Get list of organizations for incident management"""
    logger.info(f"GET /incident/organizations - integration_id: {integration_id}")

    try:
        organizations = await incident_integration_service.get_organizations(
            integration_id, offset, limit, sort
        )

        return OrganizationsResponse(
            data=organizations,
            pagination={
                "total": len(organizations),
                "limit": limit,
                "offset": offset
            }
        )
    except Exception as e:
        logger.error(f"Error listing organizations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incident/organizations/{organization_id}", response_model=Organization, tags=["Organization"])
async def get_organization(
        organization_id: str = Path(..., description="Unique identifier of the organization"),
        integration_id: str = Query(..., description="Integration ID")
):
    """Get a specific organization by ID"""
    logger.info(f"GET /incident/organizations/{organization_id}")

    try:
        organization = await incident_integration_service.get_organization(integration_id, organization_id)

        if not organization:
            raise HTTPException(status_code=404, detail=f"Organization {organization_id} not found")

        return organization
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization {organization_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Service endpoints
@router.get("/incident/{organization_id}/services", response_model=ServicesResponse, tags=["Service"])
async def list_services(
        organization_id: str = Path(..., description="Unique identifier of the organization"),
        integration_id: str = Query(..., description="Integration ID"),
        offset: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
        sort: Optional[str] = Query(None, description="Field to sort by")
):
    """Get list of services for an organization"""
    logger.info(f"GET /incident/{organization_id}/services")

    try:
        services = await incident_integration_service.get_services(
            integration_id, organization_id, offset, limit, sort
        )

        return ServicesResponse(
            data=services,
            pagination={
                "total": len(services),
                "limit": limit,
                "offset": offset
            }
        )
    except Exception as e:
        logger.error(f"Error listing services for organization {organization_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incident/{organization_id}/services/{service_id}", response_model=Service, tags=["Service"])
async def get_service(
        organization_id: str = Path(..., description="Unique identifier of the organization"),
        service_id: str = Path(..., description="Unique identifier of the service"),
        integration_id: str = Query(..., description="Integration ID")
):
    """Get a specific service by ID"""
    logger.info(f"GET /incident/{organization_id}/services/{service_id}")

    try:
        service = await incident_integration_service.get_service(integration_id, organization_id, service_id)

        if not service:
            raise HTTPException(status_code=404, detail=f"Service {service_id} not found")

        return service
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service {service_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Team endpoints
@router.get("/incident/{organization_id}/services/{service_id}/teams", response_model=TeamsResponse, tags=["Team"])
async def list_teams(
        organization_id: str = Path(..., description="Unique identifier of the organization"),
        service_id: str = Path(..., description="Unique identifier of the service"),
        integration_id: str = Query(..., description="Integration ID"),
        offset: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
        sort: Optional[str] = Query(None, description="Field to sort by")
):
    """Get list of teams for a service"""
    logger.info(f"GET /incident/{organization_id}/services/{service_id}/teams")

    try:
        teams = await incident_integration_service.get_teams(
            integration_id, organization_id, service_id, offset, limit, sort
        )

        return TeamsResponse(
            data=teams,
            pagination={
                "total": len(teams),
                "limit": limit,
                "offset": offset
            }
        )
    except Exception as e:
        logger.error(f"Error listing teams for service {service_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incident/{organization_id}/services/{service_id}/teams/{team_id}", response_model=Team, tags=["Team"])
async def get_team(
        organization_id: str = Path(..., description="Unique identifier of the organization"),
        service_id: str = Path(..., description="Unique identifier of the service"),
        team_id: str = Path(..., description="Unique identifier of the team"),
        integration_id: str = Query(..., description="Integration ID")
):
    """Get a specific team by ID"""
    logger.info(f"GET /incident/{organization_id}/services/{service_id}/teams/{team_id}")

    try:
        team = await incident_integration_service.get_team(integration_id, organization_id, service_id, team_id)

        if not team:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

        return team
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team {team_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Incident endpoints
@router.get("/incident/{organization_id}/services/{service_id}/teams/{team_id}/incidents", tags=["Incident"])
async def list_incidents(
        organization_id: str = Path(..., description="Unique identifier of the organization"),
        service_id: str = Path(..., description="Unique identifier of the service"),
        team_id: str = Path(..., description="Unique identifier of the team"),
        integration_id: str = Query(..., description="Integration ID"),
        offset: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
        sort: Optional[str] = Query(None, description="Field to sort by")
):
    """List incidents for a specific team"""
    logger.info(f"GET /incident/{organization_id}/services/{service_id}/teams/{team_id}/incidents")

    try:
        result = await incident_service.list_incidents(
            integration_id, organization_id, service_id, team_id, offset, limit, sort
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing incidents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incident/{organization_id}/services/{service_id}/teams/{team_id}/incidents", tags=["Incident"])
async def create_incident(
        organization_id: str = Path(..., description="Unique identifier of the organization"),
        service_id: str = Path(..., description="Unique identifier of the service"),
        team_id: str = Path(..., description="Unique identifier of the team"),
        incident_request: IncidentCreateRequest = ...,
        integration_id: str = Query(..., description="Integration ID")
):
    """Create a new incident"""
    logger.info(f"POST /incident/{organization_id}/services/{service_id}/teams/{team_id}/incidents")

    try:
        result = await incident_service.create_incident(
            integration_id, organization_id, service_id, team_id, incident_request
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating incident: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incident/{organization_id}/services/{service_id}/teams/{team_id}/incidents/{incident_id}",
            tags=["Incident"])
async def get_incident(
        organization_id: str = Path(..., description="Unique identifier of the organization"),
        service_id: str = Path(..., description="Unique identifier of the service"),
        team_id: str = Path(..., description="Unique identifier of the team"),
        incident_id: str = Path(..., description="Unique identifier of the incident"),
        integration_id: str = Query(..., description="Integration ID")
):
    """Get a specific incident by ID"""
    logger.info(f"GET /incident/{organization_id}/services/{service_id}/teams/{team_id}/incidents/{incident_id}")

    try:
        result = await incident_service.get_incident(
            integration_id, organization_id, service_id, team_id, incident_id
        )

        if result["status"] == "error":
            if "not found" in result["message"].lower():
                raise HTTPException(status_code=404, detail=result["message"])
            else:
                raise HTTPException(status_code=500, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting incident {incident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/incident/{organization_id}/services/{service_id}/teams/{team_id}/incidents/{incident_id}",
            tags=["Incident"])
async def update_incident(
        organization_id: str = Path(..., description="Unique identifier of the organization"),
        service_id: str = Path(..., description="Unique identifier of the service"),
        team_id: str = Path(..., description="Unique identifier of the team"),
        incident_id: str = Path(..., description="Unique identifier of the incident"),
        incident_request: IncidentUpdateRequest = ...,
        integration_id: str = Query(..., description="Integration ID")
):
    """Update an existing incident"""
    logger.info(f"PUT /incident/{organization_id}/services/{service_id}/teams/{team_id}/incidents/{incident_id}")

    try:
        result = await incident_service.update_incident(
            integration_id, organization_id, service_id, team_id, incident_id, incident_request
        )

        if result["status"] == "error":
            if "not found" in result["message"].lower():
                raise HTTPException(status_code=404, detail=result["message"])
            else:
                raise HTTPException(status_code=500, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating incident {incident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))