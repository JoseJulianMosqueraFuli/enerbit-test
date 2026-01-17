"""Configuration module.

This module loads and manages application configuration from environment variables.
"""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Config:
    POSTGRES_CONFIG: Optional[str] = os.getenv("DATABASE_URL")
    REDIS_HOST: Optional[str] = os.getenv("REDIS_HOST")
    REDIS_PORT: Optional[str] = os.getenv("REDIS_PORT")
