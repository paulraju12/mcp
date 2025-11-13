# unizo_mcp/__init__.py

"""
Unizo-MCP: Custom MCP server generator for Unizo API applications.
"""

try:
    from importlib.metadata import version
    __version__ = version("unizo-mcp")
except Exception:
    __version__ = "0.0.0.dev0"

from .server import add_mcp_server, create_mcp_server, mount_mcp_server
from .http_tools import create_mcp_tools_from_openapi
from .scoped_server import ScopedMCPServer
from .connection_context import ConnectionContext, parse_scopes_from_header

__all__ = [
    "add_mcp_server",
    "create_mcp_server",
    "mount_mcp_server",
    "create_mcp_tools_from_openapi",
    "ScopedMCPServer",
    "ConnectionContext",
    "parse_scopes_from_header",
]