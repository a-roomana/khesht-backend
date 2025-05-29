import redis.asyncio as redis

from app.settings import REDIS_URL


class RedisManager:
    """Redis connection manager for the application."""

    def __init__(self):
        self.redis_client: redis.Redis | None = None

    async def connect(self):
        """Establish connection to Redis."""
        self.redis_client = redis.from_url(
            REDIS_URL, encoding="utf-8", decode_responses=True
        )

        # Test the connection
        await self.redis_client.ping()

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

    async def get_client(self) -> redis.Redis:
        """Get Redis client instance."""
        if not self.redis_client:
            await self.connect()
        return self.redis_client


redis_manager = RedisManager()
