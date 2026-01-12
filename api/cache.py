# ---------------------------------------------------------------------------
# File    : api/cache.py
# Purpose : Caching layer for TS-ErrorsAnalysis (Stage 8)
# Version : 1.0
# License : MIT
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------
"""
Caching layer for improved performance.

Provides:
- In-memory TTL cache using cachetools
- Optional Redis backend for distributed caching
- Cache decorators for endpoint results
- Cache warming and invalidation
"""

import hashlib
import json
from typing import Any, Optional, Callable
from functools import wraps
from cachetools import TTLCache
import numpy as np

# In-memory TTL cache (5 minutes TTL, max 100 items)
_memory_cache = TTLCache(maxsize=100, ttl=300)

# Try to import Redis (optional)
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

# Redis client (lazy initialization)
_redis_client: Optional['redis.Redis'] = None


def get_redis_client() -> Optional['redis.Redis']:
    """Get or create Redis client (if available)."""
    global _redis_client

    if not HAS_REDIS:
        return None

    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=False,
                socket_connect_timeout=1
            )
            # Test connection
            _redis_client.ping()
        except Exception:
            # Redis not available, fall back to memory cache
            _redis_client = None

    return _redis_client


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.

    Args:
        prefix: Cache key prefix (typically function name)
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Hash-based cache key
    """
    # Convert numpy arrays to lists for serialization
    def serialize_value(v):
        if isinstance(v, np.ndarray):
            return v.tolist()
        return v

    args_serialized = [serialize_value(arg) for arg in args]
    kwargs_serialized = {k: serialize_value(v) for k, v in kwargs.items()}

    # Create JSON representation
    key_data = {
        'args': args_serialized,
        'kwargs': kwargs_serialized
    }

    key_json = json.dumps(key_data, sort_keys=True)
    key_hash = hashlib.md5(key_json.encode()).hexdigest()

    return f"{prefix}:{key_hash}"


def cache_result(ttl: int = 300, use_redis: bool = False):
    """
    Decorator to cache function results.

    Args:
        ttl: Time to live in seconds (default 5 minutes)
        use_redis: Whether to try using Redis (falls back to memory if unavailable)

    Usage:
        @cache_result(ttl=600)
        def expensive_function(x, y):
            return x + y
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = generate_cache_key(func.__name__, *args, **kwargs)

            # Try Redis first if requested
            if use_redis:
                redis_client = get_redis_client()
                if redis_client:
                    try:
                        cached_value = redis_client.get(cache_key)
                        if cached_value:
                            return json.loads(cached_value)
                    except Exception:
                        pass  # Fall through to memory cache or compute

            # Try memory cache
            if cache_key in _memory_cache:
                return _memory_cache[cache_key]

            # Compute result
            result = func(*args, **kwargs)

            # Store in cache
            try:
                _memory_cache[cache_key] = result

                # Also store in Redis if requested
                if use_redis:
                    redis_client = get_redis_client()
                    if redis_client:
                        try:
                            redis_client.setex(
                                cache_key,
                                ttl,
                                json.dumps(result)
                            )
                        except Exception:
                            pass  # Redis write failed, but we have memory cache
            except Exception:
                pass  # Caching failed, but we have the result

            return result

        return wrapper
    return decorator


def invalidate_cache(prefix: Optional[str] = None):
    """
    Invalidate cache entries.

    Args:
        prefix: If provided, only invalidate keys with this prefix.
                If None, clear entire cache.
    """
    global _memory_cache

    if prefix is None:
        # Clear everything
        _memory_cache.clear()

        redis_client = get_redis_client()
        if redis_client:
            try:
                redis_client.flushdb()
            except Exception:
                pass
    else:
        # Clear specific prefix (memory cache)
        keys_to_delete = [k for k in _memory_cache if k.startswith(prefix)]
        for key in keys_to_delete:
            del _memory_cache[key]

        # Clear specific prefix (Redis)
        redis_client = get_redis_client()
        if redis_client:
            try:
                pattern = f"{prefix}:*"
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
            except Exception:
                pass


def get_cache_stats() -> dict:
    """
    Get cache statistics.

    Returns:
        Dict with cache stats
    """
    stats = {
        'memory_cache': {
            'size': len(_memory_cache),
            'maxsize': _memory_cache.maxsize,
            'ttl': _memory_cache.ttl
        },
        'redis_available': HAS_REDIS and get_redis_client() is not None
    }

    # Get Redis stats if available
    if stats['redis_available']:
        redis_client = get_redis_client()
        try:
            info = redis_client.info('stats')
            stats['redis'] = {
                'keys': redis_client.dbsize(),
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0)
            }
        except Exception:
            stats['redis_available'] = False

    return stats


def warm_cache(data_samples: list, compute_func: Callable):
    """
    Pre-populate cache with common queries.

    Args:
        data_samples: List of data samples to pre-compute
        compute_func: Function to compute results (should be decorated with @cache_result)
    """
    for sample in data_samples:
        try:
            # This will populate the cache
            if isinstance(sample, dict):
                compute_func(**sample)
            elif isinstance(sample, (list, tuple)):
                compute_func(*sample)
            else:
                compute_func(sample)
        except Exception:
            pass  # Skip failed warm-ups


# Cache health check
async def check_cache_health() -> dict:
    """
    Check cache system health.

    Returns:
        Health status dict
    """
    health = {
        'memory_cache': 'healthy',
        'redis': 'not_configured'
    }

    # Check memory cache
    try:
        test_key = '__health_check__'
        _memory_cache[test_key] = True
        if _memory_cache.get(test_key):
            del _memory_cache[test_key]
        else:
            health['memory_cache'] = 'unhealthy'
    except Exception:
        health['memory_cache'] = 'unhealthy'

    # Check Redis if configured
    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_client.ping()
            health['redis'] = 'healthy'
        except Exception:
            health['redis'] = 'unhealthy'

    return health
