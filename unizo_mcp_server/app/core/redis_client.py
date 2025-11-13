# app/core/redis_client.py

"""
Redis client service for storing connection-specific data.
"""

import redis
import structlog
from typing import Optional, Dict, Any
import json

logger = structlog.getLogger(__name__)


class RedisService:
    """
    Singleton service for managing Redis connections and operations.
    """

    def __init__(self):
        """Initialize Redis service with no client."""
        self.client: Optional[redis.Redis] = None

    async def initialize(self, redis_url: str = "redis://dragonfly-svc:6379"):
        """
        Initialize Redis client.

        Args:
            redis_url: Redis connection URL
        """
        try:
            self.client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )

            # Test connection
            self.client.ping()
            logger.info("Redis client initialized successfully", redis_url=redis_url)
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {str(e)}")
            raise

    async def close(self):
        """Close Redis connection."""
        if self.client:
            self.client.close()
            logger.info("Redis client closed")

    def store_connection_data(
            self,
            connection_id: str,
            org_id: str,
            env_id: str,
            scopes: Optional[list] = None,
            suborganization_id: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
            ttl: int = 3600  # 1 hour default
    ) -> bool:
        """
        Store connection data in Redis.

        Args:
            connection_id: Unique connection identifier
            org_id: Organization ID
            env_id: Environment ID
            scopes: List of scopes for this connection
            suborganization_id: Sub-organization ID (optional, for service key auth)
            metadata: Additional metadata
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Redis client not initialized")
            return False

        try:
            key = f"mcp:connection:{connection_id}"

            data = {
                "org_id": org_id,
                "env_id": env_id,
                "suborganization_id": suborganization_id,
                "scopes": scopes or [],
                "metadata": metadata or {}
            }

            # Store as JSON string
            self.client.setex(
                key,
                ttl,
                json.dumps(data)
            )

            logger.debug(
                f"Stored connection data in Redis",
                connection_id=connection_id,
                org_id=org_id,
                env_id=env_id,
                suborganization_id=suborganization_id
            )
            return True

        except Exception as e:
            logger.error(f"Failed to store connection data: {str(e)}")
            return False

    def get_suborganization_id(self, connection_id: str) -> Optional[str]:
        """Get suborganization  ID for a connection."""
        data = self.get_connection_data(connection_id)
        return data.get("suborganization_id") if data else None


    def get_connection_data(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve connection data from Redis.

        Args:
            connection_id: Unique connection identifier

        Returns:
            Dictionary with connection data or None if not found
        """
        if not self.client:
            logger.error("Redis client not initialized")
            return None

        try:
            key = f"mcp:connection:{connection_id}"
            data = self.client.get(key)

            if data:
                parsed_data = json.loads(data)
                logger.debug(
                    f"Retrieved connection data from Redis",
                    connection_id=connection_id
                )
                return parsed_data

            logger.warning(f"Connection data not found in Redis", connection_id=connection_id)
            return None

        except Exception as e:
            logger.error(f"Failed to retrieve connection data: {str(e)}")
            return None

    def delete_connection_data(self, connection_id: str) -> bool:
        """
        Delete connection data from Redis.

        Args:
            connection_id: Unique connection identifier

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Redis client not initialized")
            return False

        try:
            key = f"mcp:connection:{connection_id}"
            result = self.client.delete(key)

            if result:
                logger.debug(f"Deleted connection data from Redis", connection_id=connection_id)
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete connection data: {str(e)}")
            return False

    def get_org_id(self, connection_id: str) -> Optional[str]:
        """Get organization ID for a connection."""
        data = self.get_connection_data(connection_id)
        return data.get("org_id") if data else None

    def get_env_id(self, connection_id: str) -> Optional[str]:
        """Get environment ID for a connection."""
        data = self.get_connection_data(connection_id)
        return data.get("env_id") if data else None

    def get_scopes(self, connection_id: str) -> Optional[list]:
        """Get scopes for a connection."""
        data = self.get_connection_data(connection_id)
        return data.get("scopes") if data else None


# Global Redis service instance
redis_service = RedisService()


async def get_redis_client() -> RedisService:
    """
    Dependency to ensure Redis client is initialized.

    Returns:
        Initialized RedisService instance
    """
    if redis_service.client is None:
        await redis_service.initialize()
    return redis_service