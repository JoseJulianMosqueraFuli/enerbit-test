"""Settings module using Pydantic BaseSettings.

This module defines all application configuration with validation.
"""

import os
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""

    # Application
    APP_NAME: str = "Service Order Management System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    DB_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(
        default=10, description="Maximum overflow connections"
    )
    DB_POOL_PRE_PING: bool = Field(
        default=True, description="Enable connection health checks"
    )

    # Redis
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database number")

    # Security
    ALLOWED_ORIGINS: List[str] = Field(
        default=["*"], description="CORS allowed origins"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=100, description="Rate limit per minute per IP"
    )
    SECRET_KEY: Optional[str] = Field(
        default=None, description="Secret key for JWT tokens"
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # AWS (optional, for deployment)
    AWS_REGION: str = Field(default="us-east-1", description="AWS region")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(
        default=None, description="AWS access key ID"
    )
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(
        default=None, description="AWS secret access key"
    )

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value.

        Args:
            v: Environment value

        Returns:
            str: Validated environment value

        Raises:
            ValueError: If environment is invalid
        """
        allowed = ["development", "staging", "production", "test"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level value.

        Args:
            v: Log level value

        Returns:
            str: Validated log level value

        Raises:
            ValueError: If log level is invalid
        """
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v_upper

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def validate_origins(cls, v: List[str], info) -> List[str]:
        """Validate CORS origins.

        Args:
            v: List of origins
            info: Validation info

        Returns:
            List[str]: Validated origins

        Raises:
            ValueError: If wildcard is used in production
        """
        environment = info.data.get("ENVIRONMENT", "development")
        if environment == "production" and "*" in v:
            raise ValueError(
                "Wildcard CORS origin (*) is not allowed in production. "
                "Please specify explicit origins."
            )
        return v

    def get_database_url(self) -> str:
        """Get database URL with pool settings.

        Returns:
            str: Database URL
        """
        return self.DATABASE_URL

    def get_redis_url(self) -> str:
        """Get Redis URL.

        Returns:
            str: Redis URL
        """
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def is_production(self) -> bool:
        """Check if running in production.

        Returns:
            bool: True if production environment
        """
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development.

        Returns:
            bool: True if development environment
        """
        return self.ENVIRONMENT == "development"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Create global settings instance
try:
    settings = Settings()
    print(f"✓ Settings loaded successfully for environment: {settings.ENVIRONMENT}")
    print(f"✓ Log level: {settings.LOG_LEVEL}")
    print(f"✓ Database pool size: {settings.DB_POOL_SIZE}")
    print(f"✓ Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
except Exception as e:
    print(f"✗ Failed to load settings: {e}")
    print("Please ensure all required environment variables are set in .env file")
    raise
