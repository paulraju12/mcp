import structlog
from typing import Dict, Any, List, Optional

from tempory.core import BaseScopedTools
from .services.integration import integration_service
from .services.ticket_service import ticket_service
from .services.user_service import user_service
from .models.ticket_models import (
    CollectionCreateRequest, CollectionType, TicketData, TicketCreateRequest,
    TicketUpdateRequest, CreateTicketBulkRequest, TicketLinkRequest
)

logger = structlog.getLogger(__name__)


class TicketingTools(BaseScopedTools):

    def __init__(self, mcp_server):
        super().__init__(mcp_server, scope='ticketing')

    def _register_tools(self):
        """Register all MCP tools for ticketing"""
        # Use consistent registration method throughout
        # Connector and integration tools
        self.register_tool(name="ticketing_list_connectors")(self.list_connectors)
        self.register_tool(name="ticketing_list_integrations")(self.list_integrations)
        self.register_tool(name="ticketing_list_organizations")(self.list_organizations)
        self.register_tool(name="ticketing_get_organization")(self.get_organization)
        self.register_tool(name="ticketing_list_collections")(self.list_collections)
        self.register_tool(name="ticketing_get_collection")(self.get_collection)
        #self.register_tool()(self.create_collection)

        # User tools
        self.register_tool(name="ticketing_list_users")(self.list_users)
        self.register_tool(name="ticketing_get_user")(self.get_user)

        # Ticket tools
        self.register_tool(name="confirm_ticket_creation")(self.confirm_ticket_creation)
        self.register_tool(name="ticketing_list_tickets")(self.list_tickets)
        self.register_tool(name="ticketing_get_ticket")(self.get_ticket)
        self.register_tool(name="ticketing_create_ticket")(self.create_ticket)
        self.register_tool(name="ticketing_create_bulk_tickets")(self.create_bulk_tickets)
        self.register_tool(name="ticketing_update_ticket")(self.update_ticket)
        self.register_tool(name="ticketing_link_tickets")(self.link_tickets)

        # Comment tools
        self.register_tool(name="ticketing_list_comments")(self.list_comments)
        self.register_tool(name="ticketing_get_comment")(self.get_comment)
        self.register_tool(name="ticketing_create_comment")(self.create_comment)

        # Attachment tools
        self.register_tool(name="ticketing_list_attachments")(self.list_attachments)
        self.register_tool(name="ticketing_get_attachment")(self.get_attachment)
        self.register_tool(name="ticketing_create_attachment")(self.create_attachment)

        # Label tools
        self.register_tool(name="ticketing_list_labels")(self.list_labels)
        self.register_tool(name="ticketing_create_label")(self.create_label)

    # Connector and Integration tools
    async def list_connectors(self) -> List[dict]:
        """Get list of available ticket connectors"""
        logger.info("MCP tool: list_connectors called")
        connectors = await integration_service.get_connectors()
        return connectors

    async def list_integrations(self, connector: str) -> List[dict]:
        """Get integrations for a specific connector"""
        logger.info(f"MCP tool: list_integrations called for connector: {connector}")
        integrations = await integration_service.get_integrations(connector)
        return integrations

    async def list_organizations(self, integration_id: str) -> List[dict]:
        """Get organizations for an integration"""
        logger.info(f"MCP tool: list_organizations called for integration: {integration_id}")
        organizations = await integration_service.get_organizations(integration_id)
        return [org.dict() for org in organizations]

    async def get_organization(self, integration_id: str, organization_id: str) -> Dict[str, Any]:
        """Get a specific organization by ID"""
        logger.info(f"MCP tool: get_organization called for org: {organization_id}")
        return await integration_service.get_organization(integration_id, organization_id)

    async def list_collections(self, integration_id: str, organization_id: str) -> List[dict]:
        """Get collections for an organization"""
        logger.info(f"MCP tool: list_collections called for integration: {integration_id}, org: {organization_id}")
        collections = await integration_service.get_collections(integration_id, organization_id)
        return [collection.dict() for collection in collections]

    async def get_collection(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str
    ) -> Dict[str, Any]:
        """Get a specific collection by ID"""
        logger.info(f"MCP tool: get_collection called for collection: {collection_id}")
        return await integration_service.get_collection(integration_id, organization_id, collection_id)

    async def create_collection(
            self,
            integration_id: str,
            organization_id: str,
            name: str,
            type: str,
            description: Optional[str] = None,
            owner_id: Optional[str] = None,
            member_ids: Optional[List[str]] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None,
            parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new collection"""
        logger.info(f"MCP tool: create_collection called with name: {name}")

        collection_request = CollectionCreateRequest(
            name=name,
            description=description,
            type=CollectionType(type),
            owner_id=owner_id,
            member_ids=member_ids,
            start_date=start_date,
            end_date=end_date,
            metadata=metadata,
            parent_id=parent_id
        )

        return await integration_service.create_collection(
            integration_id, organization_id, collection_request
        )

    # User tools
    async def list_users(
            self,
            integration_id: str,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all users"""
        logger.info(f"MCP tool: list_users called for integration: {integration_id}")
        return await user_service.list_users(integration_id, offset, limit, sort)

    async def get_user(self, integration_id: str, user_id: str) -> Dict[str, Any]:
        """Get user by identifier"""
        logger.info(f"MCP tool: get_user called for user: {user_id}")
        return await user_service.get_user(integration_id, user_id)

    # Ticket tools
    async def confirm_ticket_creation(self, user_request: str) -> Dict[str, Any]:
        """Confirm ticket creation and extract ticket details"""
        logger.info(f"MCP tool: confirm_ticket_creation called")
        return await ticket_service.confirm_ticket_creation(user_request)

    async def create_ticket(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            name: str,
            description: str,
            type: str,
            assignee_ids: Optional[List[str]] = None,
            labels: Optional[List[str]] = None,
            priority: Optional[str] = None,
            due_date: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a new ticket"""
        logger.info(f"MCP tool: create_ticket called with name: {name}")

        ticket_request = TicketCreateRequest(
            name=name,
            description=description,
            type=type,
            assignee_ids=assignee_ids,
            labels=labels,
            priority=priority,
            due_date=due_date,
            metadata=metadata
        )

        return await ticket_service.create_ticket(
            integration_id, organization_id, collection_id, ticket_request
        )

    async def create_bulk_tickets(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            tickets: List[Dict[str, Any]],
            notify: Optional[bool] = False
    ) -> Dict[str, Any]:
        """Create multiple tickets in bulk"""
        logger.info(f"MCP tool: create_bulk_tickets called with {len(tickets)} tickets")

        # Convert ticket dictionaries to TicketData objects
        ticket_data_list = [TicketData(**ticket) for ticket in tickets]

        bulk_request = CreateTicketBulkRequest(
            tickets=ticket_data_list,
            notify=notify
        )

        return await ticket_service.create_bulk_tickets(
            integration_id, organization_id, collection_id, bulk_request
        )

    async def link_tickets(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            linked_ticket_id: str,
            relationship_type: str,
            description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Link two tickets together"""
        logger.info(f"MCP tool: link_tickets called for ticket: {ticket_id}")

        link_request = TicketLinkRequest(
            linked_ticket_id=linked_ticket_id,
            relationship_type=relationship_type,
            description=description
        )

        return await ticket_service.link_tickets(
            integration_id, organization_id, collection_id, ticket_id, link_request
        )

    async def get_ticket(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str
    ) -> Dict[str, Any]:
        """Get a specific ticket"""
        logger.info(f"MCP tool: get_ticket called for ticket: {ticket_id}")
        return await ticket_service.get_ticket(
            integration_id, organization_id, collection_id, ticket_id
        )

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
        logger.info(f"MCP tool: list_tickets called for integration: {integration_id}")
        return await ticket_service.list_tickets(
            integration_id, organization_id, collection_id, offset, limit, sort
        )

    async def update_ticket(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            status: Optional[str] = None,
            priority: Optional[str] = None,
            type: Optional[str] = None,
            assignee_ids: Optional[List[str]] = None,
            labels: Optional[List[str]] = None,
            due_date: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Update an existing ticket"""
        logger.info(f"MCP tool: update_ticket called for ticket: {ticket_id}")
        try:
            ticket_request = TicketUpdateRequest(
                name=name,
                description=description,
                status=status,
                priority=priority,
                type=type,
                assignee_ids=assignee_ids,
                labels=labels,
                due_date=due_date,
                metadata=metadata
            )
            return await ticket_service.update_ticket(
                integration_id, organization_id, collection_id, ticket_id, ticket_request
            )
        except Exception as e:
            logger.error(f"Error updating ticket: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to update ticket: {str(e)}"
            }

    # Comment tools
    async def list_comments(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str
    ) -> Dict[str, Any]:
        """List all comments for a ticket"""
        logger.info(f"MCP tool: list_comments called for ticket: {ticket_id}")
        return await ticket_service.list_comments(
            integration_id, organization_id, collection_id, ticket_id
        )

    async def get_comment(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            comment_id: str
    ) -> Dict[str, Any]:
        """Get a specific comment"""
        logger.info(f"MCP tool: get_comment called for comment: {comment_id}")
        return await ticket_service.get_comment(
            integration_id, organization_id, collection_id, ticket_id, comment_id
        )

    async def create_comment(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            content: str,
            author_id: Optional[str] = None,
            is_internal: Optional[bool] = False,
            mentions: Optional[List[str]] = None,
            attachment_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a comment on a ticket"""
        logger.info(f"MCP tool: create_comment called for ticket: {ticket_id}")

        comment_request = {
            "comment": content,
            "authorId": author_id,
            "isInternal": is_internal,
            "mentions": mentions,
            "attachmentIds": attachment_ids
        }

        return await ticket_service.create_comment(
            integration_id, organization_id, collection_id, ticket_id, comment_request
        )

    # Attachment tools
    async def list_attachments(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str
    ) -> Dict[str, Any]:
        """List all attachments for a ticket"""
        logger.info(f"MCP tool: list_attachments called for ticket: {ticket_id}")
        return await ticket_service.list_attachments(
            integration_id, organization_id, collection_id, ticket_id
        )

    async def get_attachment(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            attachment_id: str
    ) -> Dict[str, Any]:
        """Get a specific attachment"""
        logger.info(f"MCP tool: get_attachment called for attachment: {attachment_id}")
        return await ticket_service.get_attachment(
            integration_id, organization_id, collection_id, ticket_id, attachment_id
        )

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
        logger.info(f"MCP tool: create_attachment called for ticket: {ticket_id}")
        return await ticket_service.create_attachment(
            integration_id, organization_id, collection_id, ticket_id,
            file_data, file_name, mime_type, description
        )

    # Label tools
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
        logger.info(f"MCP tool: list_labels called for ticket: {ticket_id}")
        return await ticket_service.list_labels(
            integration_id, organization_id, collection_id, ticket_id,
            offset, limit, sort
        )

    async def create_label(
            self,
            integration_id: str,
            organization_id: str,
            collection_id: str,
            ticket_id: str,
            name: str,
            description: Optional[str] = None,
            color: Optional[str] = None,
            category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a label on a ticket"""
        logger.info(f"MCP tool: create_label called for ticket: {ticket_id}")

        label_request = {
            "name": name,
            "description": description,
            "color": color,
            "category": category
        }

        return await ticket_service.create_label(
            integration_id, organization_id, collection_id, ticket_id, label_request
        )