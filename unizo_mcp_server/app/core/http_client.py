"""
HTTP client service for making external API requests.

This module provides a singleton HTTP client using httpx for async requests,
with connection pooling and timeout configuration for scalability.
"""

import httpx
import logging
from typing import Any, Dict, Optional
from fastapi import Depends
from .config import settings

logger = logging.getLogger(__name__)

class HTTPClientService:
    """
    Singleton service for managing HTTP client sessions.
    """

    def __init__(self):
        """Initialize the HTTP client service with no client."""
        self.client = None

    async def initialize(self):
        """Initialize the HTTP client with connection pooling and timeout."""
        limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
        self.client = httpx.AsyncClient(
            timeout=settings.request_timeout,
            limits=limits,
            follow_redirects=True,
        )
        logger.info("HTTP client initialized")

    async def close(self):
        """Close the HTTP client and release resources."""
        if self.client is not None:
            await self.client.aclose()
            self.client = None
            logger.info("HTTP client closed")

    async def make_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        json_data: Any = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request and return the parsed response.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH).
            url: The URL to request.
            headers: Request headers.
            json_data: JSON data for POST, PUT, or PATCH requests.
            params: Query parameters for the request.

        Returns:
            Parsed JSON response or text if not JSON.

        Raises:
            RuntimeError: If the client is not initialized.
            ValueError: If the HTTP method is unsupported.
            httpx.HTTPStatusError: If the response status indicates an error.
        """
        if self.client is None:
            raise RuntimeError("HTTP client not initialized")

        logger.debug(f"Making {method.upper()} request to: {url}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"JSON data: {json_data}")
        logger.debug(f"Params: {params}")

        try:
            method = method.lower()
            if method == "get":
                response = await self.client.get(url, headers=headers, params=params)
            elif method == "post":
                response = await self.client.post(url, headers=headers, json=json_data, params=params)
            elif method == "put":
                response = await self.client.put(url, headers=headers, json=json_data, params=params)
            elif method == "delete":
                response = await self.client.delete(url, headers=headers, params=params)
            elif method == "patch":
                response = await self.client.patch(url, headers=headers, json=json_data, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response text: {response.text[:500]}...")
            response.raise_for_status()

            try:
                return response.json()
            except ValueError:
                return {"text": response.text}
        except Exception as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise

# Global HTTP client service instance
http_client_service = HTTPClientService()

async def get_http_client() -> HTTPClientService:
    """
    Dependency to ensure HTTP client is initialized.

    Returns:
        Initialized HTTPClientService instance.
    """
    if http_client_service.client is None:
        await http_client_service.initialize()
    return http_client_service