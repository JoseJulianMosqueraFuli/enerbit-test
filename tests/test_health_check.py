"""Tests for health check endpoints."""

import os
os.environ["SKIP_DB_INIT"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ENVIRONMENT"] = "test"

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def health_client():
    """Create a test client for health endpoints without DB initialization."""
    from main import app
    with TestClient(app) as client:
        yield client


class TestHealthEndpoint:
    def test_health_endpoint_returns_200(self, health_client):
        response = health_client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_healthy_status(self, health_client):
        response = health_client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_endpoint_returns_version(self, health_client):
        response = health_client.get("/health")
        data = response.json()
        assert "version" in data

    def test_health_endpoint_returns_environment(self, health_client):
        response = health_client.get("/health")
        data = response.json()
        assert "environment" in data


class TestReadinessEndpoint:
    def test_readiness_endpoint_with_dependencies(self, health_client):
        response = health_client.get("/ready")
        assert response.status_code in [200, 503]

    def test_readiness_endpoint_returns_dependencies_status(self, health_client):
        response = health_client.get("/ready")
        data = response.json()
        assert "dependencies" in data
        assert "database" in data["dependencies"]
        assert "redis" in data["dependencies"]

    def test_readiness_endpoint_returns_version(self, health_client):
        response = health_client.get("/ready")
        data = response.json()
        assert "version" in data

    def test_readiness_endpoint_200_when_all_healthy(self, health_client):
        response = health_client.get("/ready")
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "ready"

    def test_readiness_endpoint_503_when_unhealthy(self, health_client):
        response = health_client.get("/ready")
        if response.status_code == 503:
            data = response.json()
            assert data["status"] == "not_ready"
