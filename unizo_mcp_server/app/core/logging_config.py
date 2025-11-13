"""
Logging configuration for the Unizo API application.

This module sets up structured logging with structlog, including JSON output,
request context, and log rotation for production use.
"""

import logging
import structlog
import logging.handlers
import os
import tempfile
from typing import Any, Dict
from fastapi import Request, FastAPI
from .config import settings
import uuid


def configure_logging():
    """
    Configure structured logging with structlog for production use.

    Sets up JSON logging with request context, log rotation, and appropriate log levels.
    """
    # Configure standard logging with proper file handling
    try:
        # Try to create log file in current directory first
        log_file = "unizo_api.log"
        # Test if we can write to current directory
        test_path = os.path.join(os.getcwd(), "test_write")
        with open(test_path, 'w') as f:
            f.write("test")
        os.remove(test_path)

        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10_000_000, backupCount=5
        )
    except (PermissionError, OSError):
        # If we can't write to current directory, use temp directory
        log_dir = tempfile.gettempdir()
        log_file = os.path.join(log_dir, "unizo_api.log")

        try:
            handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10_000_000, backupCount=5
            )
        except (PermissionError, OSError):
            # If all file logging fails, just use console logging
            handler = logging.StreamHandler()
            print(f"Warning: Could not create log file. Logging to console only.")

    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(message)s",
        handlers=[handler, logging.StreamHandler()]
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_request_context_processor():
    """
    Create a structlog processor to add request context (e.g., request ID).

    Returns:
        A processor function that adds request metadata to logs.
    """
    def add_request_context(logger: Any, method: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add request ID and other context to log events.

        Args:
            logger: The logger instance.
            method: The logging method (e.g., info, error).
            event_dict: The log event dictionary.

        Returns:
            Updated event dictionary with request context.
        """
        request_id = structlog.contextvars.get_contextvars().get("request_id", "N/A")
        event_dict["request_id"] = request_id
        return event_dict
    return add_request_context


def setup_request_context_middleware(app: FastAPI):
    """
    Add middleware to inject request ID into logs.

    Args:
        app: The FastAPI application instance.
    """
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """
        Middleware to add a unique request ID to each request's log context.

        Args:
            request: The incoming FastAPI request.
            call_next: The next middleware or route handler.

        Returns:
            The response from the next handler.
        """
        request_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)
        try:
            response = await call_next(request)
            return response
        finally:
            structlog.contextvars.clear_contextvars()