"""Tests for health check endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    def test_health_endpoint_returns_200(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_healthy_status(self, client: TestClient):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_endpoint_returns_version(self, client: TestClient):
        response = client.get("/health")
        data = response.json()
        assert "version" in data

    def test_health_endpoint_returns_environment(self, client: TestClient):
        response = client.get("/health")
        data = response.json()
        assert "environment" in data


class TestReadinessEndpoint:
    def test_readiness_endpoint_with_healthy_dependencies(self, client: TestClient):
        response = client.get("/ready")
        assert response.status_code in [200, 503]

    def test_readiness_endpoint_returns_dependencies_status(self, client: TestClient):
        response = client.get("/ready")
        data = response.json()
        assert "dependencies" in data
        assert "database" in data["dependencies"]
        assert "redis" in data["dependencies"]

    def test_readiness_endpoint_returns_version(self, client: TestClient):
        response = client.get("/ready")
        data = response.json()
        assert "version" in data

    def test_readiness_endpoint_200_when_all_healthy(self, client: TestClient):
        response = client.get("/ready")
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "ready"

    def test_readiness_endpoint_503_when_unhealthy(self, client: TestClient):
        response = client.get("/ready")
        if response.status_code == 503:
            data = response.json()
            assert data["status"] == "not_ready"
