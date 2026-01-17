"""Error handling module.

This module defines custom exception classes and error handlers for the application.
"""

import logging
import traceback
from typing import Any, Dict

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError as SQLAlchemyDatabaseError
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database errors."""

    def __init__(self, message: str = "Database error occurred"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    """Custom exception for resource not found errors."""

    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        self.message = f"{resource} with id {identifier} not found"
        super().__init__(self.message)


async def database_error_handler(
    request: Request, exc: DatabaseError
) -> JSONResponse:
    """Handle database errors with 503 status and retry-after header.

    Args:
        request: The incoming request
        exc: The database error exception

    Returns:
        JSONResponse: Error response with 503 status
    """
    logger.error(f"Database error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database service temporarily unavailable"},
        headers={"Retry-After": "60"},
    )


async def sqlalchemy_database_error_handler(
    request: Request, exc: SQLAlchemyDatabaseError
) -> JSONResponse:
    """Handle SQLAlchemy database errors.

    Args:
        request: The incoming request
        exc: The SQLAlchemy database error

    Returns:
        JSONResponse: Error response with 503 status
    """
    logger.error(f"SQLAlchemy database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database service temporarily unavailable"},
        headers={"Retry-After": "60"},
    )


async def sqlalchemy_operational_error_handler(
    request: Request, exc: OperationalError
) -> JSONResponse:
    """Handle SQLAlchemy operational errors (connection issues).

    Args:
        request: The incoming request
        exc: The operational error

    Returns:
        JSONResponse: Error response with 503 status
    """
    logger.error(f"Database connection error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database connection failed"},
        headers={"Retry-After": "30"},
    )


async def validation_error_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with detailed messages.

    Args:
        request: The incoming request
        exc: The validation error

    Returns:
        JSONResponse: Error response with 400 status
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(f"Validation error: {errors}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Validation error", "errors": errors},
    )


async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """Handle resource not found errors.

    Args:
        request: The incoming request
        exc: The not found error

    Returns:
        JSONResponse: Error response with 404 status
    """
    logger.info(f"Resource not found: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": exc.message,
            "resource": exc.resource,
            "identifier": exc.identifier,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions with logging.

    Args:
        request: The incoming request
        exc: The unhandled exception

    Returns:
        JSONResponse: Error response with 500 status
    """
    # Log full stack trace
    logger.error(
        f"Unhandled exception: {str(exc)}\n"
        f"Request: {request.method} {request.url}\n"
        f"Traceback: {traceback.format_exc()}"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


class CircuitBreaker:
    """Circuit breaker pattern implementation for external service calls."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open

    def call(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Any: Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        import time

        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.warning(
                    f"Circuit breaker opened after {self.failure_count} failures"
                )

            raise e


# Global circuit breaker for Redis operations
redis_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)


class EventQueue:
    """Local event queue for when Redis is unavailable."""

    def __init__(self):
        """Initialize event queue."""
        self.queue: list = []

    def add_event(self, event_data: Dict[str, Any]) -> None:
        """Add event to local queue.

        Args:
            event_data: Event data to queue
        """
        self.queue.append(event_data)
        logger.info(f"Event queued locally: {event_data.get('id', 'unknown')}")

    def get_events(self) -> list:
        """Get all queued events.

        Returns:
            list: All queued events
        """
        return self.queue.copy()

    def clear_events(self) -> None:
        """Clear all queued events."""
        self.queue.clear()


# Global event queue
event_queue = EventQueue()
