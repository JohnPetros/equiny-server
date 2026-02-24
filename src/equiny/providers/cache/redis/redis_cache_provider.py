from redis import Redis

from equiny.core.shared.interfaces.cache_provider import CacheProvider
from equiny.constants import Env


class RedisCacheProvider(CacheProvider):
    _redis: Redis

    def __init__(self) -> None:
        self._redis = Redis.from_url(Env.REDIS_URL)  # type: ignore[reportUnknownMemberType]

    def get(self, key: str) -> str | None:
        value = self._redis.get(key)
        if isinstance(value, str):
            return value
        return None

    def set(self, key: str, value: str) -> None:
        self._redis.set(key, value)

    def delete(self, key: str) -> None:
        self._redis.delete(key)
