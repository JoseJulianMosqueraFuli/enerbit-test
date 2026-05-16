"""Tests for middleware."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

from middleware import LoggingMiddleware


class TestLoggingMiddleware:
    def test_middleware_adds_correlation_id(self, client: TestClient):
        response = client.get("/health")
        assert "X-Correlation-ID" in response.headers

    def test_middleware_uses_provided_correlation_id(self, client: TestClient):
        correlation_id = "test-correlation-123"
        response = client.get(
            "/health", headers={"X-Correlation-ID": correlation_id}
        )
        assert response.headers["X-Correlation-ID"] == correlation_id

    def test_middleware_generates_correlation_id_if_not_provided(self, client: TestClient):
        response = client.get("/health")
        assert response.headers["X-Correlation-ID"] is not None
        assert len(response.headers["X-Correlation-ID"]) > 0

    def test_middleware_works_with_all_endpoints(self, client: TestClient):
        endpoints = ["/health", "/ready", "/v1/customers/", "/v1/work_orders/"]
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert "X-Correlation-ID" in response.headers
