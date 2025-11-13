# app/core/base_tools.py

"""
Base tools class for scope-aware tool registration.
"""

import structlog
from typing import Callable, Optional
from mcp.server.fastmcp import FastMCP

from unizo_mcp_server.unizo_mcp.scoped_server import ScopedMCPServer

logger = structlog.getLogger(__name__)


class BaseScopedTools:
    """Base class for scope-aware MCP tool registration"""

    def __init__(self, mcp_server: FastMCP, scope: str):
        """
        Initialize the tools with scope metadata.

        Args:
            mcp_server: The MCP server instance
            scope: The scope/category this tool belongs to
        """
        self.mcp_server = mcp_server
        self.scope = scope.lower()

        self.is_scoped = isinstance(mcp_server, ScopedMCPServer)

        logger.info(
            f"Initializing tools for scope: {self.scope}",
            is_scoped=self.is_scoped
        )

        self._register_tools()

    def _register_tools(self):
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement _register_tools()")

    def register_tool(self, name: str, metadata: Optional[dict] = None):
        """
        Decorator to register a tool with scope metadata.
        """

        def decorator(func: Callable) -> Callable:
            registered_func = self.mcp_server.tool(name=name)(func)

            if self.is_scoped:
                self.mcp_server.register_tool_with_scope(
                    tool_name=name,
                    scope=self.scope,
                    metadata=metadata
                )

            logger.debug(f"Registered tool: {name} with scope: {self.scope}")

            return registered_func

        return decorator