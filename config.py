"""Configuration module.

This module provides backward compatibility with the old Config class.
For new code, use settings.py directly.
"""

from settings import settings


class Config:
    """Legacy configuration class for backward compatibility."""

    POSTGRES_CONFIG = settings.DATABASE_URL
    REDIS_HOST = settings.REDIS_HOST
    REDIS_PORT = str(settings.REDIS_PORT)

