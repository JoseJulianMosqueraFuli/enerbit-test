"""Middleware module.

This module defines custom middleware for the application.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from logger import StructuredLogger, clear_correlation_id, set_correlation_id

logger = StructuredLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with timing and correlation IDs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response: Response from handler
        """
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        correlation_id = set_correlation_id(correlation_id)

        # Add correlation ID to request state
        request.state.correlation_id = correlation_id

        # Record start time
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log request
        logger.log_request(
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration=duration,
            correlation_id=correlation_id,
        )

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        # Clear correlation ID
        clear_correlation_id()

        return response
