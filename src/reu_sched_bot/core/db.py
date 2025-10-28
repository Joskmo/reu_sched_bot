from redis.asyncio import Redis, from_url as redis_from_url
from ..config import RedisSettings

redis_config = RedisSettings()
redis: Redis = redis_from_url(
    url = redis_config.url,
    encoding="utf-8",
)
