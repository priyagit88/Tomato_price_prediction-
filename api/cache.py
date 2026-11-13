"""
Redis caching client with local in-memory fallback for high-throughput daily predictions.
"""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger("api.cache")

class CacheManager:
    def __init__(self):
        self._memory_cache = {}
        self._redis_client = None
        self._redis_available = False
        
        try:
            import redis
            import os
            host = os.getenv("REDIS_HOST", "localhost")
            port = int(os.getenv("REDIS_PORT", "6379"))
            password = os.getenv("REDIS_PASSWORD", None)
            enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
            
            if enabled:
                self._redis_client = redis.Redis(
                    host=host,
                    port=port,
                    password=password if password else None,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                self._redis_client.ping()
                self._redis_available = True
                logger.info("Connected to Azure Cache for Redis.")
        except Exception as e:
            logger.info("Redis not configured or unreachable (%s). Using in-memory cache.", e)
            self._redis_available = False

    def get(self, key: str) -> Optional[Any]:
        if self._redis_available and self._redis_client:
            try:
                val = self._redis_client.get(key)
                if val:
                    return json.loads(val)
            except Exception:
                pass
        return self._memory_cache.get(key)

    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        if self._redis_available and self._redis_client:
            try:
                self._redis_client.setex(key, ttl_seconds, json.dumps(value))
                return
            except Exception:
                pass
        self._memory_cache[key] = value

    def clear(self):
        self._memory_cache.clear()
        if self._redis_available and self._redis_client:
            try:
                self._redis_client.flushdb()
            except Exception:
                pass

cache_manager = CacheManager()

