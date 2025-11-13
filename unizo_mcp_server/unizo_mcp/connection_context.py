# unizo_mcp/connection_context.py

"""
Connection context management for scope-based filtering.
"""

import structlog
from typing import Optional, List, Dict, Any
from contextvars import ContextVar, Token

logger = structlog.getLogger(__name__)

CONNECTION_CONTEXT: ContextVar[Optional["ConnectionContext"]] = ContextVar(
    "connection_context", default=None
)


class ConnectionContext:
    """Manages connection-specific context including scopes"""

    # Make CONNECTION_CONTEXT accessible as class attribute
    CONNECTION_CONTEXT = CONNECTION_CONTEXT

    def __init__(
            self,
            connection_id: str,
            scopes: Optional[List[str]] = None,
            metadata: Optional[Dict[str, Any]] = None
    ):
        self.connection_id = connection_id
        self.scopes = [s.strip().lower() for s in scopes] if scopes else None
        self.metadata = metadata or {}

        logger.info(
            "Created connection context",
            connection_id=connection_id,
            scopes=self.scopes,
        )

    def has_scope(self, scope: str) -> bool:
        """Check if connection has a specific scope"""
        if self.scopes is None:
            return True
        return scope.lower() in self.scopes

    def has_any_scope(self, scopes: List[str]) -> bool:
        """Check if connection has any of the specified scopes"""
        if self.scopes is None:
            return True
        return any(scope.lower() in self.scopes for scope in scopes)

    @classmethod
    def get_current(cls) -> Optional["ConnectionContext"]:
        """Get the current connection context"""
        return CONNECTION_CONTEXT.get()

    @classmethod
    def set_current(cls, context: "ConnectionContext") -> Token:
        """Set the current connection context and return token"""
        return CONNECTION_CONTEXT.set(context)

    @classmethod
    def clear_current(cls):
        """Clear the current connection context"""
        CONNECTION_CONTEXT.set(None)


def parse_scopes_from_header(header_value: str) -> Optional[List[str]]:
    """Parse scopes from header value"""
    if not header_value:
        return None

    header_value = header_value.strip()

    # Try JSON array format
    if header_value.startswith("[") and header_value.endswith("]"):
        try:
            import json
            return json.loads(header_value)
        except:
            pass

    # Try comma or space separated
    if "," in header_value:
        return [s.strip() for s in header_value.split(",") if s.strip()]
    else:
        return [s.strip() for s in header_value.split() if s.strip()]