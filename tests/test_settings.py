"""Tests for settings configuration."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from settings import Settings


class TestSettingsValidation:
    def test_valid_environment_values(self):
        for env in ["development", "staging", "production", "test"]:
            settings = Settings(
                DATABASE_URL="postgresql://test:test@localhost/test",
                ENVIRONMENT=env,
            )
            assert settings.ENVIRONMENT == env

    def test_invalid_environment_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                DATABASE_URL="postgresql://test:test@localhost/test",
                ENVIRONMENT="invalid",
            )
        assert "Environment must be one of" in str(exc_info.value)

    def test_valid_log_levels(self):
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = Settings(
                DATABASE_URL="postgresql://test:test@localhost/test",
                LOG_LEVEL=level,
            )
            assert settings.LOG_LEVEL == level

    def test_lowercase_log_level_converted_to_uppercase(self):
        settings = Settings(
            DATABASE_URL="postgresql://test:test@localhost/test",
            LOG_LEVEL="debug",
        )
        assert settings.LOG_LEVEL == "DEBUG"

    def test_invalid_log_level_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                DATABASE_URL="postgresql://test:test@localhost/test",
                LOG_LEVEL="VERBOSE",
            )
        assert "Log level must be one of" in str(exc_info.value)

    def test_wildcard_origins_allowed_in_development(self):
        settings = Settings(
            DATABASE_URL="postgresql://test:test@localhost/test",
            ENVIRONMENT="development",
            ALLOWED_ORIGINS=["*"],
        )
        assert settings.ALLOWED_ORIGINS == ["*"]

    def test_wildcard_origins_not_allowed_in_production(self):
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                DATABASE_URL="postgresql://test:test@localhost/test",
                ENVIRONMENT="production",
                ALLOWED_ORIGINS=["*"],
            )
        assert "Wildcard CORS origin" in str(exc_info.value)

    def test_specific_origins_allowed_in_production(self):
        settings = Settings(
            DATABASE_URL="postgresql://test:test@localhost/test",
            ENVIRONMENT="production",
            ALLOWED_ORIGINS=["https://example.com"],
        )
        assert settings.ALLOWED_ORIGINS == ["https://example.com"]


class TestSettingsDefaults:
    def test_default_app_name(self):
        settings = Settings(DATABASE_URL="postgresql://test:test@localhost/test")
        assert settings.APP_NAME == "Service Order Management System"

    def test_default_app_version(self):
        settings = Settings(DATABASE_URL="postgresql://test:test@localhost/test")
        assert settings.APP_VERSION == "1.0.0"

    def test_default_database_url_required(self):
        with pytest.raises(ValidationError):
            Settings()

    def test_default_redis_host(self):
        settings = Settings(DATABASE_URL="postgresql://test:test@localhost/test")
        assert settings.REDIS_HOST == "localhost"

    def test_default_redis_port(self):
        settings = Settings(DATABASE_URL="postgresql://test:test@localhost/test")
        assert settings.REDIS_PORT == 6379

    def test_default_rate_limit(self):
        settings = Settings(DATABASE_URL="postgresql://test:test@localhost/test")
        assert settings.RATE_LIMIT_PER_MINUTE == 100


class TestSettingsHelperMethods:
    def test_get_database_url(self):
        url = "postgresql://user:pass@localhost/db"
        settings = Settings(DATABASE_URL=url)
        assert settings.get_database_url() == url

    def test_get_redis_url(self):
        settings = Settings(
            DATABASE_URL="postgresql://test:test@localhost/test",
            REDIS_HOST="redis.example.com",
            REDIS_PORT=6380,
            REDIS_DB=2,
        )
        assert settings.get_redis_url() == "redis://redis.example.com:6380/2"

    def test_is_production_true(self):
        settings = Settings(
            DATABASE_URL="postgresql://test:test@localhost/test",
            ENVIRONMENT="production",
        )
        assert settings.is_production() is True

    def test_is_production_false(self):
        settings = Settings(
            DATABASE_URL="postgresql://test:test@localhost/test",
            ENVIRONMENT="development",
        )
        assert settings.is_production() is False

    def test_is_development_true(self):
        settings = Settings(
            DATABASE_URL="postgresql://test:test@localhost/test",
            ENVIRONMENT="development",
        )
        assert settings.is_development() is True

    def test_is_development_false(self):
        settings = Settings(
            DATABASE_URL="postgresql://test:test@localhost/test",
            ENVIRONMENT="production",
        )
        assert settings.is_development() is False
