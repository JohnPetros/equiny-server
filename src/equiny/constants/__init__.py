from .env import Env as EnvClass
from .cache_keys import CacheKeys

Env = EnvClass()  # pyright: ignore[reportCallIssue]
CACHE_KEYS = CacheKeys()

__all__ = ['Env', 'CACHE_KEYS']
