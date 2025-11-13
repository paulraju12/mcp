# app/main.py

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI

from unizo_mcp_server.unizo_mcp import add_mcp_server

from tempory.core import settings
from tempory.core.middleware import add_kong_middleware
from tempory.core import http_client_service
from tempory.core.logging_config import configure_logging, setup_request_context_middleware
from .categories.ticketing.endpoints import router as ticketing_router
from .categories.ticketing.tools import TicketingTools
from .categories.platform.tools import PlatformTools
from .categories.identity.tools import IdentityTools
from .categories.incident.tools import IncidentTools
from .categories.scm.tools import SCMTools
from .categories.pcr.tools import PCRTools
from unizo_mcp_server.app.categories.comms.tools import CommsTools
from .categories.key_management.tools import KeyManagementTools
from .categories.vms.tools import VMSTools
from .categories.observability.tools import ObservabilityTools
from .categories.infra.tools import InfraTools
from .categories.edr.tools import EDRTools
from .categories.file_storage.tools import StorageTools
from tempory.core import redis_service

configure_logging()
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[None]:
    await http_client_service.initialize()
    await redis_service.initialize(settings.redis_url)  # Initialize Redis
    logger.info("Application started with dynamic scope filtering")
    try:
        yield
    finally:
        await http_client_service.close()
        logger.info("Application shutdown")

app = FastAPI(
    title="Unizo MCP API",
    version="1.0.0",
    description="API for managing MCP operations with dynamic scope filtering",
    lifespan=app_lifespan
)

setup_request_context_middleware(app)
add_kong_middleware(app)

# Create MCP server with dynamic scoping enabled
mcp_server = add_mcp_server(
    app,
    mount_path="/mcp",
    name="Unizo MCP",
    description="MCP server for UNIZO operations with dynamic scope filtering",
    enable_scoping=True,
    scope_header_name="x-mcp-scopes",
)

# Register ALL tools
TicketingTools(mcp_server)
PlatformTools(mcp_server)
IdentityTools(mcp_server)
IncidentTools(mcp_server)
SCMTools(mcp_server)
PCRTools(mcp_server)
CommsTools(mcp_server)
KeyManagementTools(mcp_server)
VMSTools(mcp_server)
ObservabilityTools(mcp_server)
InfraTools(mcp_server)
EDRTools(mcp_server)
StorageTools(mcp_server)


app.include_router(ticketing_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "unizo_mcp_server.app.main:app",
        host="0.0.0.0",
        port=8999,
        log_level="debug",
        reload=False
    )