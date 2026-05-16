"""Tests for work order router API endpoints."""

import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestCreateWorkOrderEndpoint:
    def test_create_work_order_success(
        self, client: TestClient, sample_customer, sample_work_order_data
    ):
        response = client.post(
            "/v1/work_orders/",
            json=sample_work_order_data,
            params={"is_active": True},
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Test Work Order"
        assert data["status"] == "new"

    def test_create_work_order_missing_fields(self, client: TestClient, sample_customer):
        response = client.post(
            "/v1/work_orders/",
            json={"title": "Test"},
            params={"is_active": True},
        )
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, 422]


class TestUpdateWorkOrderEndpoint:
    def test_update_work_order_success(
        self, client: TestClient, sample_work_order
    ):
        now = datetime.utcnow()
        updated_data = {
            "title": "Updated Title",
            "planned_date_begin": (now + timedelta(hours=2)).isoformat(),
            "planned_date_end": (now + timedelta(hours=5)).isoformat(),
            "status": "done",
        }
        response = client.put(
            f"/v1/work_orders/{sample_work_order.id}",
            json=updated_data,
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "updated successfully" in response.json()["message"]

    def test_update_work_order_not_found(self, client: TestClient):
        now = datetime.utcnow()
        updated_data = {
            "title": "Updated",
            "planned_date_begin": (now + timedelta(hours=2)).isoformat(),
            "planned_date_end": (now + timedelta(hours=5)).isoformat(),
            "status": "new",
        }
        response = client.put(f"/v1/work_orders/{uuid.uuid4()}", json=updated_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestFinishWorkOrderEndpoint:
    def test_finish_work_order_success(
        self, client: TestClient, sample_work_order
    ):
        response = client.put(f"/v1/work_orders/{sample_work_order.id}/status/done")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "updated successfully" in response.json()["message"]

    def test_finish_work_order_not_found(self, client: TestClient):
        response = client.put(f"/v1/work_orders/{uuid.uuid4()}/status/done")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetAllWorkOrdersEndpoint:
    def test_get_all_work_orders_empty(self, client: TestClient):
        response = client.get("/v1/work_orders/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_all_work_orders(self, client: TestClient, multiple_work_orders):
        response = client.get("/v1/work_orders/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3


class TestGetOrdersByStatusOrDateEndpoint:
    def test_get_orders_by_status(
        self, client: TestClient, sample_customer
    ):
        now = datetime.utcnow()
        order = WorkOrder(
            customer_id=sample_customer.id,
            title="Test",
            planned_date_begin=now,
            planned_date_end=now + timedelta(hours=3),
            status="new",
        )
        from models import WorkOrder
        from tests.conftest import db_session

        response = client.get("/v1/work_orders/status-or-date", params={"status": "new"})
        assert response.status_code == status.HTTP_200_OK

    def test_get_orders_without_params_returns_error(self, client: TestClient):
        response = client.get("/v1/work_orders/status-or-date")
        assert response.status_code == status.HTTP_200_OK
        assert "error" in response.json()


class TestGetWorkOrderByIdEndpoint:
    def test_get_work_order_by_id_success(
        self, client: TestClient, sample_work_order
    ):
        response = client.get(f"/v1/work_orders/{sample_work_order.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_work_order.id)

    def test_get_work_order_by_id_not_found(self, client: TestClient):
        response = client.get(f"/v1/work_orders/{uuid.uuid4()}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteWorkOrderEndpoint:
    def test_delete_work_order_success(
        self, client: TestClient, sample_work_order
    ):
        response = client.delete(f"/v1/work_orders/{sample_work_order.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_work_order_not_found(self, client: TestClient):
        response = client.delete(f"/v1/work_orders/{uuid.uuid4()}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
