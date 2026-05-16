"""Tests for security headers middleware."""

from fastapi.testclient import TestClient


class TestSecurityHeadersMiddleware:
    def test_strict_transport_security(self, client: TestClient):
        response = client.get("/health")
        assert "Strict-Transport-Security" in response.headers
        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
        assert "includeSubDomains" in response.headers["Strict-Transport-Security"]

    def test_x_content_type_options(self, client: TestClient):
        response = client.get("/health")
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_x_frame_options(self, client: TestClient):
        response = client.get("/health")
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_x_xss_protection(self, client: TestClient):
        response = client.get("/health")
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    def test_content_security_policy(self, client: TestClient):
        response = client.get("/health")
        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

    def test_referrer_policy(self, client: TestClient):
        response = client.get("/health")
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_permissions_policy(self, client: TestClient):
        response = client.get("/health")
        assert "Permissions-Policy" in response.headers
        assert "geolocation=()" in response.headers["Permissions-Policy"]
        assert "microphone=()" in response.headers["Permissions-Policy"]
        assert "camera=()" in response.headers["Permissions-Policy"]

    def test_security_headers_on_all_endpoints(self, client: TestClient):
        endpoints = ["/health", "/ready"]
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert "Strict-Transport-Security" in response.headers
            assert "X-Content-Type-Options" in response.headers
            assert "X-Frame-Options" in response.headers
