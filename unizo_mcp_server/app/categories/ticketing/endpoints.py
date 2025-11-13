from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Request, Query
from .models.ticket_models import (
    Organization, OrganizationsResponse, Collection, CollectionsResponse,
    CollectionCreateRequest, TicketData, TicketSummary, TicketsResponse,Connector, Integration
)
from .services.integration import IntegrationService, integration_service
from .services.ticket_service import TicketService, ticket_service

router = APIRouter(prefix="/ticketing", tags=["ticketing"])

@router.get("/services", operation_id="list_services", summary="Get list of available ticket services")
async def list_services_endpoint(request: Request) -> List[Connector]:
    services = await integration_service.get_services()
    return services

@router.get("/integrations/{service}", operation_id="list_integrations", summary="Get integrations for a specific service")
async def list_integrations_endpoint(service: str, request: Request) -> List[Integration]:
    integrations = await integration_service.get_integrations(service)
    return integrations

@router.get("/organizations/{integration_id}", operation_id="list_organizations",
         summary="Get organizations for an integration")
async def list_organizations_endpoint(integration_id: str, request: Request) -> List[Organization]:
    organizations = await integration_service.get_organizations(integration_id)
    return organizations

@router.get("/collections/{integration_id}/{organization_id}", operation_id="list_collections",
         summary="Get collections for an organization")
async def list_collections_endpoint(integration_id: str, organization_id: str, request: Request) -> List[Collection]:
    collections = await integration_service.get_collections(integration_id, organization_id)
    return collections

@router.get("/confirm_ticket_creation", operation_id="confirm_ticket_creation",
         summary="Confirm ticket creation and extract ticket details")
async def confirm_ticket_creation_endpoint(user_request: str, request: Request) -> Dict[str, Any]:
    return await ticket_service.confirm_ticket_creation(user_request)

@router.post("/create_ticket", operation_id="create_ticket", summary="Create a new ticket")
async def create_ticket_endpoint(
        integration_id: str,
        organization_id: str,
        collection_id: str,
        ticket_name: str,
        request: Request,
        ticket_description: Optional[str] = None,
        ticket_status: Optional[str] = None,
        ticket_priority: Optional[str] = None,
        ticket_type: Optional[str] = None
) -> Dict[str, Any]:
    return await ticket_service.create_ticket(
        integration_id, organization_id, collection_id, ticket_name,
        ticket_description, ticket_status, ticket_priority, ticket_type
    )

@router.get("/list_tickets", operation_id="list_tickets", summary="List tickets from a collection")
async def list_tickets_endpoint(
        integration_id: str,
        request: Request,
        organization_id: Optional[str] = None,
        collection_id: Optional[str] = None
) -> Dict[str, Any]:
    return await ticket_service.list_tickets(integration_id, organization_id, collection_id)


@router.patch("/{organization_id}/collections/{collection_id}/tickets/{ticket_id}",
             operation_id="update_ticket",
             summary="Update an existing ticket",
             response_model=Dict[str, Any])
async def update_ticket_endpoint(
    organization_id: str,
    collection_id: str,
    ticket_id: str,
    ticket_request: TicketData,
    request: Request,
    integration_id: Optional[str] = Query(None, description="Integration ID")
) -> Dict[str, Any]:
    """Update an existing ticket with new information."""
    return await ticket_service.update_ticket(organization_id, collection_id, ticket_id, ticket_request, request, integration_id)