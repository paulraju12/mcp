import traceback
import structlog
from typing import Dict, Any, Optional

from .integration import integration_service
from tempory.core import settings
from tempory.core import http_client_service
from tempory.core import extract_headers_from_request
from ..models.ticket_models import (
    TicketSummary, TicketCreateRequest, TicketUpdateRequest,
    CreateTicketBulkRequest, TicketLinkRequest, User, ChangeLog
)
from ....text_parser import extract_ticket_details_from_text

logger = structlog.getLogger(__name__)


class TicketService:
    async def confirm_ticket_creation(self, user_request: str) -> Dict[str, Any]:
        """Confirm ticket creation and extract ticket details"""
        logger.info(f"Confirming ticket creation for request: {user_request[:50]}...")
        try:
            ticket_details = await extract_ticket_details_from_text(user_request)
            connectors = await integration_service.get_connectors()

            # Set defaults
            ticket_details.status = ticket_details.status or "open"
            ticket_details.priority = ticket_details.priority or "high"
            ticket_details.type = ticket_details.type or "task"

            result = {
                "status": "success",
                "ticket_details": ticket_details.dict(),
                "connectors":connectors,
                "next_step": "select_service",
                "message": "Ticket details extracted. Please select a service to continue."
            }

            logger.info("Ticket details confirmed successfully")
            return result
        except Exception as e:
            logger.error(f"Error confirming ticket creation: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_ticket(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_request: TicketCreateRequest
    ) -> Dict[str, Any]:
        """Create a new ticket"""
        logger.info(f"Creating ticket with name: {ticket_request.name}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets"
            response = await http_client_service.make_request("post", url, headers, json_data=ticket_request.dict())

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                response_data = response.json()
            else:
                response_data = response  # Already a dict

            ticket_id = response_data.get("id", "unknown")

            result = {
                "status": "success",
                "message": f"Ticket created successfully with ID: {ticket_id}",
                "ticket": response_data
            }

            logger.info(f"Ticket created successfully: {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_bulk_tickets(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            bulk_request: CreateTicketBulkRequest
    ) -> Dict[str, Any]:
        """Create multiple tickets in bulk"""
        logger.info(f"Creating {len(bulk_request.tickets)} tickets in bulk")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets/bulk"
            response = await http_client_service.make_request("post", url, headers, json_data=bulk_request.dict())

            result = {
                "status": "success",
                "message": f"Successfully created {len(bulk_request.tickets)} tickets",
                "tickets": response if isinstance(response, list) else response.get("data", [])
            }

            logger.info(f"Bulk tickets created successfully")
            return result
        except Exception as e:
            logger.error(f"Error creating bulk tickets: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def link_tickets(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            link_request: TicketLinkRequest
    ) -> Dict[str, Any]:
        """Link two tickets together"""
        logger.info(f"Linking tickets: {link_request.source_ticket_id} -> {link_request.target_ticket_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets/link"
            response = await http_client_service.make_request("post", url, headers, json_data=link_request.dict())

            result = {
                "status": "success",
                "message": f"Successfully linked tickets",
                "link": response
            }

            logger.info(f"Tickets linked successfully")
            return result
        except Exception as e:
            logger.error(f"Error linking tickets: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_ticket(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str
    ) -> Dict[str, Any]:
        """Get a specific ticket by ID"""
        logger.info(f"Getting ticket: {ticket_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets/{ticket_id}"
            response = await http_client_service.make_request("get", url, headers)

            result = {
                "status": "success",
                "message": "Ticket retrieved successfully",
                "ticket": response
            }

            logger.info(f"Ticket retrieved successfully: {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting ticket: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def list_tickets(
            self,
            integration_id: str,
            organization_id: Optional[str] = None,
            collection_id: Optional[str] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List tickets from a collection"""
        logger.info(f"Listing tickets for integration: {integration_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            # Auto-select organization if not provided
            if organization_id is None:
                organizations = await integration_service.get_organizations(integration_id)
                if len(organizations) == 0:
                    return {
                        "status": "error",
                        "message": "No organizations found for this integration"
                    }
                elif len(organizations) == 1:
                    organization_id = organizations[0].id
                    logger.info(f"Auto-selected single organization: {organization_id}")
                else:
                    return {
                        "status": "select_organization",
                        "message": "Multiple organizations found. Please select one:",
                        "organizations": [org.dict() for org in organizations],
                        "integration_id": integration_id
                    }

            # Auto-select collection if not provided
            if collection_id is None:
                collections = await integration_service.get_collections(integration_id, organization_id)
                if len(collections) == 0:
                    return {
                        "status": "error",
                        "message": f"No collections found for organization: {organization_id}"
                    }
                elif len(collections) == 1:
                    collection_id = collections[0].id
                    logger.info(f"Auto-selected single collection: {collection_id}")
                else:
                    return {
                        "status": "select_collection",
                        "message": "Multiple collections found. Please select one:",
                        "collections": [coll.dict() for coll in collections],
                        "integration_id": integration_id,
                        "organization_id": organization_id
                    }

            # Build query parameters
            params = {}
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if sort is not None:
                params["sort"] = sort

            # Get tickets
            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets"
            response = await http_client_service.make_request("get", url, headers, params=params)

            # Handle response whether it's already a dict or needs to be parsed
            if hasattr(response, 'json'):
                tickets_data = response.json().get("data", [])
                pagination = response.json().get("pagination")
            else:
                tickets_data = response.get("data", [])  # Already a dict
                pagination = response.get("pagination")

            ticket_summaries = [
                TicketSummary(
                    id=ticket.get("id", "unknown"),
                    name=ticket.get("name", "Unnamed Ticket"),
                    type=ticket.get("type", "Unknown"),
                    status=ticket.get("status", "Unknown"),
                    description=ticket.get("description"),
                    key=ticket.get("key"),
                    assignees=[User(**assignee) for assignee in ticket.get("assignees" or [])],
                    target_url=ticket.get("targetUrl"),
                    change_log=ChangeLog(**ticket.get("changeLog", {})) if ticket.get("changeLog") else None
                )
                for ticket in tickets_data
            ]

            result = {
                "status": "success",
                "message": f"Found {len(ticket_summaries)} tickets in collection",
                "tickets": [ticket.dict() for ticket in ticket_summaries],
                "pagination": pagination,
                "collection_info": {
                    "integration_id": integration_id,
                    "organization_id": organization_id,
                    "collection_id": collection_id
                }
            }

            logger.info(f"Successfully retrieved {len(ticket_summaries)} tickets")
            return result
        except Exception as e:
            logger.error(f"Error listing tickets: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def update_ticket(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            ticket_request: TicketUpdateRequest
    ) -> Dict[str, Any]:
        """Update an existing ticket"""
        logger.info(f"Updating ticket {ticket_id} in collection: {collection_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets/{ticket_id}"
            response = await http_client_service.make_request(
                "put", url, headers, json_data=ticket_request.dict(exclude_none=True)
            )

            logger.info(f"Updated ticket: {ticket_id}")
            return {
                "status": "success",
                "message": "Ticket updated successfully",
                "ticket": response
            }
        except Exception as e:
            logger.error(f"Error updating ticket: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to update ticket: {str(e)}"
            }

    # Comment-related methods
    async def list_comments(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str
    ) -> Dict[str, Any]:
        """List all comments for a ticket"""
        logger.info(f"Listing comments for ticket: {ticket_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets/{ticket_id}/comments"
            response = await http_client_service.make_request("get", url, headers)

            result = {
                "status": "success",
                "message": "Comments retrieved successfully",
                "comments": response.get("data", []),
                "pagination": response.get("pagination")
            }

            logger.info(f"Retrieved comments for ticket: {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Error listing comments: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_comment(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            comment_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a comment on a ticket"""
        logger.info(f"Creating comment on ticket: {ticket_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets/{ticket_id}/comments"
            response = await http_client_service.make_request("post", url, headers, json_data=comment_request)

            result = {
                "status": "success",
                "message": "Comment created successfully",
                "comment": response
            }

            logger.info(f"Comment created on ticket: {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_comment(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            comment_id: str
    ) -> Dict[str, Any]:
        """Get a specific comment"""
        logger.info(f"Getting comment: {comment_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets/{ticket_id}/comments/{comment_id}"
            response = await http_client_service.make_request("get", url, headers)

            result = {
                "status": "success",
                "message": "Comment retrieved successfully",
                "comment": response
            }

            logger.info(f"Comment retrieved: {comment_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting comment: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # Attachment-related methods
    async def list_attachments(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str
    ) -> Dict[str, Any]:
        """List all attachments for a ticket"""
        logger.info(f"Listing attachments for ticket: {ticket_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets/{ticket_id}/attachments"
            response = await http_client_service.make_request("get", url, headers)

            result = {
                "status": "success",
                "message": "Attachments retrieved successfully",
                "attachments": response.get("data", []),
                "pagination": response.get("pagination")
            }

            logger.info(f"Retrieved attachments for ticket: {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Error listing attachments: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_attachment(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            file_data: bytes,
            file_name: str,
            mime_type: str,
            description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an attachment on a ticket"""
        logger.info(f"Creating attachment on ticket: {ticket_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            # Prepare multipart form data
            files = {
                'file': (file_name, file_data, mime_type)
            }
            data = {
                'fileName': file_name,
                'fileSize': len(file_data),
                'mimeType': mime_type
            }
            if description:
                data['description'] = description

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets/{ticket_id}/attachments"
            response = await http_client_service.make_request("post", url, headers, files=files, data=data)

            result = {
                "status": "success",
                "message": "Attachment created successfully",
                "attachment": response
            }

            logger.info(f"Attachment created on ticket: {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Error creating attachment: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_attachment(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            attachment_id: str
    ) -> Dict[str, Any]:
        """Get a specific attachment"""
        logger.info(f"Getting attachment: {attachment_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets/{ticket_id}/attachments/{attachment_id}"
            response = await http_client_service.make_request("get", url, headers)

            result = {
                "status": "success",
                "message": "Attachment retrieved successfully",
                "attachment": response
            }

            logger.info(f"Attachment retrieved: {attachment_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting attachment: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # Label-related methods
    async def list_labels(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all labels for a ticket"""
        logger.info(f"Listing labels for ticket: {ticket_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            # Build query parameters
            params = {}
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if sort is not None:
                params["sort"] = sort

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets/{ticket_id}/labels"
            response = await http_client_service.make_request("get", url, headers, params=params)

            result = {
                "status": "success",
                "message": "Labels retrieved successfully",
                "labels": response.get("data", []),
                "pagination": response.get("pagination")
            }

            logger.info(f"Retrieved labels for ticket: {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Error listing labels: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def create_label(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            label_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a label on a ticket"""
        logger.info(f"Creating label on ticket: {ticket_id}")
        try:
            headers = extract_headers_from_request()
            headers["integrationId"] = integration_id

            url = f"{settings.ticketing_api_base_url}/api/v1/ticketing/{organization_id}/collections/{collection_id}/tickets/{ticket_id}/labels"
            response = await http_client_service.make_request("post", url, headers, json_data=label_request)

            result = {
                "status": "success",
                "message": "Label created successfully",
                "label": response
            }

            logger.info(f"Label created on ticket: {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Error creating label: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


ticket_service = TicketService()