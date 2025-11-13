# unizo_mcp/server.py

"""
Server module for Unizo-MCP with dynamic scope support.
"""

from typing import Dict, Optional, Any
import uuid

from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

from .http_tools import create_mcp_tools_from_openapi
from .scoped_server import ScopedMCPServer
from .connection_context import ConnectionContext, parse_scopes_from_header
from tempory.app.core import redis_service

import structlog

logger = structlog.getLogger(__name__)


def create_mcp_server(
        app: FastAPI,
        name: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        enable_scoping: bool = True,
) -> FastMCP:
    """
    Create an MCP server from a FastAPI app.

    Args:
        app: The FastAPI application
        name: Name for the MCP server
        description: Description for the MCP server
        capabilities: Optional capabilities for the MCP server
        enable_scoping: Whether to enable dynamic scope filtering

    Returns:
        The created FastMCP or ScopedMCPServer instance
    """
    server_name = name or app.title or "UNIZO MCP"
    server_description = description or app.description

    base_mcp_server = FastMCP(server_name, server_description)

    if capabilities:
        for capability, value in capabilities.items():
            base_mcp_server.settings.capabilities[capability] = value

    if enable_scoping:
        mcp_server = ScopedMCPServer(base_mcp_server)
        logger.info("Created ScopedMCPServer with dynamic filtering")
    else:
        mcp_server = base_mcp_server
        logger.info("Created standard MCP server")

    return mcp_server


def mount_mcp_server(
        app: FastAPI,
        mcp_server: FastMCP,
        mount_path: str = "/mcp",
        serve_tools: bool = True,
        base_url: Optional[str] = None,
        describe_all_responses: bool = False,
        describe_full_response_schema: bool = False,
        scope_header_name: str = "x-mcp-scopes",
) -> None:
    """
    Mount an MCP server to a FastAPI app with scope support.

    Args:
        app: The FastAPI application
        mcp_server: The MCP server to mount
        mount_path: Path where the MCP server will be mounted
        serve_tools: Whether to serve tools from the FastAPI app
        base_url: Base URL for API requests
        describe_all_responses: Whether to include all response schemas
        describe_full_response_schema: Whether to include full response schema
        scope_header_name: Name of the header containing scope information
    """
    if not mount_path.startswith("/"):
        mount_path = f"/{mount_path}"
    if mount_path.endswith("/"):
        mount_path = mount_path[:-1]

    sse_transport = SseServerTransport(f"{mount_path}/messages/")
    is_scoped = isinstance(mcp_server, ScopedMCPServer)
    actual_server = mcp_server.base_server if is_scoped else mcp_server

    async def handle_mcp_connection(request: Request):
        connection_id = str(uuid.uuid4())

        # Extract headers
        org_id = (request.headers.get("x-organization-id") or
                  request.headers.get("organizationid"))
        env_id = (request.headers.get("x-environment-id") or
                  request.headers.get("environmentid"))

        # NEW: Extract suborganization ID (from service key)
        suborganization_id = (request.headers.get("x-suborganization-id") or
                              request.headers.get("suborganizationid"))

        # Extract scopes - FIX THIS LINE
        scopes = None
        if is_scoped:
            scope_header = request.headers.get(scope_header_name, "")  # Get actual header value
            logger.info(f"Raw scope header received: '{scope_header}'")
            scopes = parse_scopes_from_header(scope_header)  # ← FIXED: Pass actual value, not ...

            logger.info(
                "New MCP connection",
                connection_id=connection_id,
                scopes=scopes,
                org_id=org_id,
                env_id=env_id,
                suborganization_id=suborganization_id,
                client=request.client.host if request.client else "unknown"
            )

            # Set scopes on server instance
            mcp_server.set_active_scopes(scopes)


        redis_service.store_connection_data(
            connection_id=connection_id,
            org_id=org_id,
            env_id=env_id,
            scopes=scopes,
            suborganization_id=suborganization_id,
            metadata={
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "auth_type": "service_key" if suborganization_id else "api_key"
            },
            ttl=3600
        )

        # Also create ConnectionContext for backward compatibility
        context = ConnectionContext(
            connection_id=connection_id,
            scopes=scopes,
            metadata={"org_id": org_id, "env_id": env_id}
        )
        token = ConnectionContext.set_current(context)

        try:
            async with sse_transport.connect_sse(
                    request.scope, request.receive, request._send
            ) as streams:
                await actual_server._mcp_server.run(
                    streams[0],
                    streams[1],
                    actual_server._mcp_server.create_initialization_options(),
                )
        finally:
            # Cleanup
            if is_scoped:
                mcp_server.set_active_scopes(None)

            # Delete from Redis
            redis_service.delete_connection_data(connection_id)

            ConnectionContext.CONNECTION_CONTEXT.reset(token)
            logger.info("MCP connection closed", connection_id=connection_id)

    if serve_tools:
        create_mcp_tools_from_openapi(
            app,
            mcp_server,
            base_url,
            describe_all_responses=describe_all_responses,
            describe_full_response_schema=describe_full_response_schema,
        )

    app.get(mount_path)(handle_mcp_connection)
    app.mount(f"{mount_path}/messages/", app=sse_transport.handle_post_message)


def add_mcp_server(
        app: FastAPI,
        mount_path: str = "/mcp",
        name: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        serve_tools: bool = True,
        base_url: Optional[str] = None,
        describe_all_responses: bool = False,
        describe_full_response_schema: bool = False,
        enable_scoping: bool = True,
        scope_header_name: str = "x-mcp-scopes",
) -> FastMCP:
    """
    Add an MCP server to a FastAPI app with scope support.

    Args:
        app: The FastAPI application
        mount_path: Path where the MCP server will be mounted
        name: Name for the MCP server
        description: Description for the MCP server
        capabilities: Optional capabilities for the MCP server
        serve_tools: Whether to serve tools from the FastAPI app
        base_url: Base URL for API requests
        describe_all_responses: Whether to include all response schemas
        describe_full_response_schema: Whether to include full response schema
        enable_scoping: Whether to enable dynamic scope filtering
        scope_header_name: Name of the header containing scope information

    Returns:
        The FastMCP or ScopedMCPServer instance
    """
    mcp_server = create_mcp_server(
        app, name, description, capabilities, enable_scoping
    )

    mount_mcp_server(
        app,
        mcp_server,
        mount_path,
        serve_tools,
        base_url,
        describe_all_responses,
        describe_full_response_schema,
        scope_header_name,
    )

    return mcp_server