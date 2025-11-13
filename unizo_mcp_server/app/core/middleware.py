import structlog
from typing import Dict
from contextvars import ContextVar
from fastapi import Request, HTTPException, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from .redis_client import redis_service

logger = structlog.getLogger(__name__)

# ContextVar for Kong headers
KONG_HEADERS: ContextVar[Dict[str, str]] = ContextVar("kong_headers", default={})


class KongHeaderContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        headers = {
            key.lower(): value for key, value in request.headers.items()
            if key.lower() in [
                "x-organization-id", "x-org-id", "organizationid", "organization-id",
                "x-environment-id", "x-env-id", "environmentid", "environment-id",
                "x-suborganization-id", "suborganizationid", "suborganization-id",
                "x-kong-request-id", "x-forwarded-for", "x-real-ip",
                "x-integration-id", "integrationid",
                "x-api-key", "mcp-api-key", "authorization"
            ]
        }
        logger.debug(f"Storing Kong headers in contextvars: {headers}")

        org_id = headers.get("x-organization-id") or headers.get("x-org-id") or \
                 headers.get("organizationid") or headers.get("organization-id")
        env_id = headers.get("x-environment-id") or headers.get("x-env-id") or \
                 headers.get("environmentid") or headers.get("environment-id")

        # NEW: Extract suborganization ID (from service key)
        suborganization_id = (headers.get("x-suborganization-id") or
                              headers.get("suborganizationid") or
                              headers.get("suborganization-id"))

        if not org_id or not env_id:
            logger.error(f"Missing required headers: organizationId={org_id}, environmentId={env_id}")
            raise HTTPException(status_code=400, detail="Missing required headers: organizationId and environmentId")

        # Store in request state for access during request lifecycle
        request.state.org_id = org_id
        request.state.env_id = env_id
        request.state.suborganization_id = suborganization_id
        request.state.headers = headers

        logger.debug(
            f"Stored in request.state: org={org_id}, env={env_id}, suborganization_id={suborganization_id}"
        )

        response = await call_next(request)
        return response


def add_kong_middleware(app: FastAPI):
    """Add Kong middleware to the FastAPI app"""
    app.add_middleware(KongHeaderContextMiddleware)