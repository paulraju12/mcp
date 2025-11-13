import structlog
from typing import Dict, List, Optional, Union
from fastapi import Request, HTTPException
from ..middleware import KONG_HEADERS
from ..redis_client import redis_service

logger = structlog.getLogger(__name__)


def get_header(headers_source: Union[Request, Dict[str, str], None], header_names: List[str],
               default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Extract header value from various sources"""
    for header_name in header_names:
        if headers_source is None:
            context_headers = KONG_HEADERS.get({})
            value = context_headers.get(header_name.lower())
            if value:
                logger.debug(f"Found header {header_name} in ContextVar: {value}")
                return value
        if isinstance(headers_source, Request):
            value = headers_source.headers.get(header_name.lower())
            if value:
                logger.debug(f"Found header {header_name} in Request: {value}")
                return value
        elif isinstance(headers_source, dict):
            value = headers_source.get(header_name.lower())
            if value:
                logger.debug(f"Found header {header_name} in dictionary: {value}")
                return value

    if required and not default:
        logger.error(f"No header found for {header_names}")
        raise HTTPException(status_code=400, detail=f"Missing required header: {', '.join(header_names)}")
    return default


def extract_headers_from_request(
        request: Optional[Request] = None,
        connection_id: Optional[str] = None
) -> Dict[str, str]:
    """
    Extract and build headers for API requests.

    Priority order:
    1. Request object (REST endpoints)
    2. connection_id parameter (explicit)
    3. ContextVar → Redis (automatic fallback)
    """

    org_id = None
    env_id = None
    suborganization_id = None

    # PRIORITY 1: Request object (REST endpoints)
    if request and hasattr(request.state, 'org_id'):
        org_id = request.state.org_id
        env_id = request.state.env_id
        suborganization_id = getattr(request.state, 'suborganization_id', None)
        # FIX: Changed from debug to info
        logger.info(f"Got headers from request.state: org={org_id}, env={env_id}, suborg={suborganization_id}")

    # PRIORITY 2: Explicit connection_id (when passed)
    elif connection_id:
        from ..redis_client import redis_service
        data = redis_service.get_connection_data(connection_id)
        if not data:
            raise HTTPException(
                status_code=400,
                detail=f"Connection data not found in Redis for connection_id: {connection_id}"
            )
        org_id = data["org_id"]
        env_id = data["env_id"]
        suborganization_id = data.get("suborganization_id")
        # FIX: Changed from debug to info
        logger.info(f"Got headers from Redis (explicit): org={org_id}, env={env_id}, suborg={suborganization_id}")

    # PRIORITY 3: Try ContextVar → Redis (automatic fallback for MCP tools)
    else:
        # Import here to avoid circular dependency
        try:
            from ....unizo_mcp.connection_context import ConnectionContext
            from ..redis_client import redis_service

            # Try to get connection_id from ContextVar
            context = ConnectionContext.get_current()

            if context and context.connection_id:
                ctx_connection_id = context.connection_id
                # FIX: Changed from debug to info
                logger.info(f"Found connection_id in ContextVar: {ctx_connection_id}")

                # Fetch from Redis
                data = redis_service.get_connection_data(ctx_connection_id)
                if data:
                    org_id = data["org_id"]
                    env_id = data["env_id"]
                    suborganization_id = data.get("suborganization_id")
                    # FIX: Changed from debug to info
                    logger.info(
                        f"Got headers from Redis via ContextVar: org={org_id}, env={env_id}, suborg={suborganization_id}"
                    )
                else:
                    logger.warning(f"Connection data not found in Redis for {ctx_connection_id}")
            else:
                logger.warning("No ConnectionContext found in ContextVar")
        except Exception as e:
            logger.error(f"Error accessing ContextVar/Redis: {str(e)}")

    # Final validation
    if not org_id or not env_id:
        raise HTTPException(
            status_code=400,
            detail="Could not retrieve connection data. Please reconnect."
        )

    # Build headers
    headers = {
        "organizationId": org_id,
        "environmentId": env_id,
        "sourcechannel": "INTERNAL",
        "Content-Type": "application/json"
    }

    #  CRITICAL FIX #1: Changed from "externalKey" to "suborganizationId"
    # CRITICAL FIX #2: Changed from debug to info for visibility
    if suborganization_id:
        headers["suborganizationId"] = suborganization_id
        logger.info(f"Added suborganizationId to headers: {suborganization_id}")
    else:
        logger.warning("No suborganization_id found - filter will NOT be applied!")

    # Add optional headers from request if available
    if request and hasattr(request.state, 'headers'):
        state_headers = request.state.headers

        integration_id = state_headers.get("x-integration-id") or state_headers.get("integrationid")
        if integration_id:
            headers["integrationId"] = integration_id

        kong_headers_list = ["x-kong-request-id", "x-forwarded-for", "x-real-ip"]
        for kong_header in kong_headers_list:
            value = state_headers.get(kong_header)
            if value:
                headers[kong_header] = value

        api_key = (state_headers.get("x-api-key") or
                   state_headers.get("mcp-api-key") or
                   state_headers.get("authorization"))
        if api_key:
            if api_key.startswith("Bearer "):
                headers["Authorization"] = api_key
            else:
                headers["X-API-Key"] = api_key

    # FIX: Changed from debug to info
    logger.info(f"Final built headers: {headers}")
    return headers