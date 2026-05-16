"""Tests for analytics router API endpoints."""

from datetime import datetime, timedelta

from fastapi import status
from fastapi.testclient import TestClient
from models import Customer, WorkOrder


class TestAverageDurationEndpoint:
    def test_average_duration_empty(self, client: TestClient):
        response = client.get("/v1/analytics/average-duration")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "average_duration" in data

    def test_average_duration_with_data(
        self, client: TestClient, db_session, sample_customer
    ):
        now = datetime.utcnow()
        order = WorkOrder(
            customer_id=sample_customer.id,
            title="Test",
            planned_date_begin=now,
            planned_date_end=now + timedelta(hours=4),
            status="done",
        )
        db_session.add(order)
        db_session.commit()

        response = client.get("/v1/analytics/average-duration")
        assert response.status_code == status.HTTP_200_OK


class TestOrderFrequencyEndpoint:
    def test_order_frequency_empty(self, client: TestClient):
        response = client.get("/v1/analytics/order-frequency")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_order_frequency_with_data(
        self, client: TestClient, db_session, sample_customer, multiple_work_orders
    ):
        response = client.get("/v1/analytics/order-frequency")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert "customer_id" in data[0]
        assert "order_count" in data[0]


class TestCustomerActivityEndpoint:
    def test_customer_activity_empty(self, client: TestClient):
        response = client.get("/v1/analytics/customer-activity")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_customer_activity_with_data(
        self, client: TestClient, db_session, sample_customer
    ):
        now = datetime.utcnow()
        for i in range(3):
            order = WorkOrder(
                customer_id=sample_customer.id,
                title=f"Order {i}",
                planned_date_begin=now,
                planned_date_end=now + timedelta(hours=3),
                status="new",
            )
            db_session.add(order)
        db_session.commit()

        response = client.get("/v1/analytics/customer-activity")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1


class TestActiveCustomersEndpoint:
    def test_active_customers(self, client: TestClient, db_session):
        now = datetime.utcnow()
        start = (now - timedelta(days=30)).isoformat()
        end = now.isoformat()

        response = client.get(
            "/v1/analytics/active-customers", params={"start": start, "end": end}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "active_customer_count" in data

    def test_active_customers_invalid_date_format(self, client: TestClient):
        response = client.get(
            "/v1/analytics/active-customers",
            params={"start": "invalid-date", "end": "also-invalid"},
        )
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, 422, 500]


class TestAverageDurationImageEndpoint:
    def test_average_duration_image(self, client: TestClient):
        response = client.get("/v1/analytics/average-duration-img")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"


class TestOrderFrequencyImageEndpoint:
    def test_order_frequency_image(self, client: TestClient):
        response = client.get("/v1/analytics/order-frequency/image")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"


class TestCustomerActivityImageEndpoint:
    def test_customer_activity_image(self, client: TestClient):
        response = client.get("/v1/analytics/customer-activity/image")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"


class TestActiveCustomersImageEndpoint:
    def test_active_customers_image(self, client: TestClient, db_session):
        now = datetime.utcnow()
        start = (now - timedelta(days=30)).isoformat()
        end = now.isoformat()

        response = client.get(
            "/v1/analytics/active-customers/image",
            params={"start": start, "end": end},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"
