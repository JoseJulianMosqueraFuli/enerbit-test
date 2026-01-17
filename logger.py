"""Structured logging module.

This module configures structured JSON logging with correlation IDs.
"""

import logging
import sys
import time
import uuid
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger


class CorrelationIdFilter(logging.Filter):
    """Filter to add correlation ID to log records."""

    def __init__(self):
        """Initialize correlation ID filter."""
        super().__init__()
        self.correlation_id: Optional[str] = None

    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to log record.

        Args:
            record: Log record to filter

        Returns:
            bool: Always True to allow all records
        """
        record.correlation_id = self.correlation_id or "no-correlation-id"
        return True


# Global correlation ID filter
correlation_filter = CorrelationIdFilter()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add custom fields to log record.

        Args:
            log_record: Log record dictionary
            record: Original log record
            message_dict: Message dictionary
        """
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = self.formatTime(record, self.datefmt)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["correlation_id"] = getattr(record, "correlation_id", "no-correlation-id")


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured JSON logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create handler
    handler = logging.StreamHandler(sys.stdout)

    # Create formatter
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s %(correlation_id)s"
    )
    handler.setFormatter(formatter)

    # Add correlation ID filter
    handler.addFilter(correlation_filter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(handler)


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Set correlation ID for current request.

    Args:
        correlation_id: Correlation ID to set, generates new if None

    Returns:
        str: The correlation ID
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_filter.correlation_id = correlation_id
    return correlation_id


def clear_correlation_id() -> None:
    """Clear correlation ID after request."""
    correlation_filter.correlation_id = None


class StructuredLogger:
    """Structured logger for application events."""

    def __init__(self, name: str):
        """Initialize structured logger.

        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        correlation_id: str,
    ) -> None:
        """Log HTTP request with timing.

        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration: Request duration in seconds
            correlation_id: Request correlation ID
        """
        self.logger.info(
            "HTTP request",
            extra={
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration * 1000, 2),
                "correlation_id": correlation_id,
            },
        )

    def log_query(self, query: str, duration: float, correlation_id: str) -> None:
        """Log database query with execution time.

        Args:
            query: SQL query
            duration: Query duration in seconds
            correlation_id: Request correlation ID
        """
        # Redact sensitive data from query
        redacted_query = self._redact_sensitive_data(query)

        self.logger.debug(
            "Database query",
            extra={
                "query": redacted_query,
                "duration_ms": round(duration * 1000, 2),
                "correlation_id": correlation_id,
            },
        )

    def log_error(
        self, error: Exception, context: Dict[str, Any], correlation_id: str
    ) -> None:
        """Log error with context.

        Args:
            error: Exception that occurred
            context: Additional context
            correlation_id: Request correlation ID
        """
        self.logger.error(
            f"Error: {str(error)}",
            extra={
                "error_type": type(error).__name__,
                "context": context,
                "correlation_id": correlation_id,
            },
            exc_info=True,
        )

    def _redact_sensitive_data(self, text: str) -> str:
        """Redact sensitive data from text.

        Args:
            text: Text to redact

        Returns:
            str: Redacted text
        """
        import re

        # Redact common sensitive patterns
        patterns = [
            (r"password['\"]?\s*[:=]\s*['\"]?([^'\"]+)['\"]?", "password=***"),
            (r"token['\"]?\s*[:=]\s*['\"]?([^'\"]+)['\"]?", "token=***"),
            (r"api[_-]?key['\"]?\s*[:=]\s*['\"]?([^'\"]+)['\"]?", "api_key=***"),
            (r"secret['\"]?\s*[:=]\s*['\"]?([^'\"]+)['\"]?", "secret=***"),
        ]

        redacted = text
        for pattern, replacement in patterns:
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)

        return redacted


# Initialize default logger
setup_logging()
