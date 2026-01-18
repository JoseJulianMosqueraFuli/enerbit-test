"""Quick test script for health check endpoints."""

import sys
from fastapi.testclient import TestClient

# Import the app
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test /health endpoint."""
    response = client.get("/health")
    print(f"Health endpoint status: {response.status_code}")
    print(f"Health endpoint response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health endpoint test passed")

def test_ready_endpoint():
    """Test /ready endpoint."""
    response = client.get("/ready")
    print(f"Ready endpoint status: {response.status_code}")
    print(f"Ready endpoint response: {response.json()}")
    # May be 200 or 503 depending on database/redis availability
    assert response.status_code in [200, 503]
    print("✓ Ready endpoint test passed")

if __name__ == "__main__":
    try:
        test_health_endpoint()
        test_ready_endpoint()
        print("\n✓ All health check tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
