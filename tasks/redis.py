"""Redis client module.

This module configures the Redis client for event streaming with circuit breaker protection.
"""

import logging
from typing import Any, Dict, Optional

import redis

from config import Config

logger = logging.getLogger(__name__)

redis_host = Config.REDIS_HOST
redis_port = Config.REDIS_PORT

try:
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    # Test connection
    redis_client.ping()
    logger.info("Redis connection established successfully")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Will use event queue fallback.")
    redis_client = None


def safe_redis_xadd(
    stream_name: str, event_data: Dict[str, Any]
) -> Optional[str]:
    """Safely add event to Redis stream with circuit breaker and fallback.

    Args:
        stream_name: Name of the Redis stream
        event_data: Event data to add

    Returns:
        Optional[str]: Event ID if successful, None otherwise
    """
    from error_handlers import event_queue, redis_circuit_breaker

    if redis_client is None:
        logger.warning("Redis client not available, queuing event locally")
        event_queue.add_event(event_data)
        return None

    try:
        event_id = redis_circuit_breaker.call(
            redis_client.xadd, stream_name, event_data
        )
        logger.info(f"Event added to Redis stream {stream_name}: {event_id}")
        return event_id
    except Exception as e:
        logger.error(f"Failed to add event to Redis: {e}. Queuing locally.")
        event_queue.add_event(event_data)
        return None
