from redis import Redis

from equiny.constants import ENV
from equiny.core.shared.interfaces.cache_provider import CacheProvider


class RedisCacheProvider(CacheProvider):
    _redis: Redis

    def __init__(self) -> None:
        self._redis = Redis.from_url(  # pyright: ignore[reportUnknownMemberType]
            ENV.REDIS_URL,
            decode_responses=True,
        )

    def get(self, key: str) -> str | None:
        value = self._redis.get(key)
        if isinstance(value, str):
            return value
        return None

    def set(self, key: str, value: str) -> None:
        self._redis.set(key, value)

    def delete(self, key: str) -> None:
        self._redis.delete(key)
