# unizo_mcp/scoped_server.py

"""
Scoped MCP server that filters tools based on connection context.
"""

import structlog
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool
from .connection_context import ConnectionContext


logger = structlog.getLogger(__name__)


class ScopedMCPServer:
    """
    Wrapper around FastMCP that provides scope-based tool filtering.
    """

    def __init__(self, base_server: FastMCP):
        self.base_server = base_server
        self._tool_metadata: Dict[str, Dict[str, Any]] = {}
        self._active_scopes: Optional[List[str]] = None

        #Get the actual tool manager
        self._tool_manager = base_server._tool_manager

        # Store original list_tools method from tool manager
        logger.info(f"Original tool_manager.list_tools: {self._tool_manager.list_tools}")
        self._original_list_tools = self._tool_manager.list_tools

        # Replace the tool manager's list_tools method
        self._tool_manager.list_tools = self._create_scoped_list_tools()
        logger.info(f"Replaced tool_manager.list_tools with scoped version")

        logger.info("Initialized ScopedMCPServer with tool_manager patching")

    def set_active_scopes(self, scopes: Optional[List[str]]):
        """Set the active scopes for this server instance"""
        self._active_scopes = scopes
        logger.info(f"Set active scopes on server: {scopes}")

    def register_tool_with_scope(
            self,
            tool_name: str,
            scope: str,
            metadata: Optional[Dict[str, Any]] = None
    ):
        """Register tool metadata including its scope"""
        self._tool_metadata[tool_name] = {
            "scope": scope.lower(),
            "metadata": metadata or {}
        }
        logger.debug(f"Registered tool {tool_name} with scope {scope}")

    def _create_scoped_list_tools(self):
        """Create the scoped list_tools function with proper closure"""
        original_list_tools = self._original_list_tools
        tool_metadata = self._tool_metadata
        server_instance = self

        def _scoped_list_tools() -> List[Tool]:
            """
            List tools filtered by current connection's scopes.
            """
            logger.info("=" * 80)
            logger.info("SCOPED LIST_TOOLS CALLED FROM TOOL_MANAGER!")
            logger.info("=" * 80)

            # Try to get context from ContextVar first
            context = ConnectionContext.get_current()

            # If no context from ContextVar, use server instance scopes
            active_scopes = None
            if context and context.scopes:
                active_scopes = context.scopes
                logger.info(f"Got scopes from ConnectionContext: {active_scopes}")
            elif server_instance._active_scopes:
                active_scopes = server_instance._active_scopes
                logger.info(f"Got scopes from server instance: {active_scopes}")
            else:
                logger.info("No scopes found anywhere!")

            all_tools = original_list_tools()

            logger.info(f"Active scopes: {active_scopes}")
            logger.info(f"Total tools before filtering: {len(all_tools)}")
            logger.info(f"Tool metadata registered: {len(tool_metadata)} tools")

            if all_tools:
                logger.info(f"Sample tool names: {[t.name for t in all_tools[:5]]}")

            if not active_scopes:
                logger.warning(f"NO SCOPING ACTIVE - returning all {len(all_tools)} tools")
                return all_tools

            filtered_tools = []
            excluded_count = 0

            for tool in all_tools:
                tool_name = tool.name

                if tool_name in tool_metadata:
                    tool_scope = tool_metadata[tool_name]["scope"]

                    if tool_scope in [s.lower() for s in active_scopes]:
                        filtered_tools.append(tool)
                        logger.info(f"✓ INCLUDE: {tool_name} (scope: {tool_scope})")
                    else:
                        excluded_count += 1
                        logger.info(f"✗ EXCLUDE: {tool_name} (scope: {tool_scope} NOT in {active_scopes})")
                else:
                    filtered_tools.append(tool)
                    logger.info(f"✓ INCLUDE: {tool_name} (no scope - default)")

            logger.info("=" * 80)
            logger.info(
                f"FILTERING RESULT: {len(filtered_tools)}/{len(all_tools)} tools "
                f"(excluded: {excluded_count}) for scopes: {active_scopes}"
            )
            logger.info("=" * 80)

            return filtered_tools

        return _scoped_list_tools

    def __getattr__(self, name):
        """Proxy all other attributes to base server"""
        return getattr(self.base_server, name)