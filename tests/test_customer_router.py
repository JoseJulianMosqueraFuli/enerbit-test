"""Tests for customer router API endpoints."""

import uuid

import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestCreateCustomerEndpoint:
    def test_create_customer_success(self, client: TestClient, sample_customer_data):
        response = client.post("/v1/customers/", json=sample_customer_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"

    def test_create_customer_missing_fields(self, client: TestClient):
        response = client.post("/v1/customers/", json={"first_name": "John"})
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, 422]

    def test_create_customer_empty_body(self, client: TestClient):
        response = client.post("/v1/customers/", json={})
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, 422]


class TestUpdateCustomerEndpoint:
    def test_update_customer_success(self, client: TestClient, sample_customer):
        updated_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "address": "New Address",
        }
        response = client.put(f"/v1/customers/{sample_customer.id}", json=updated_data)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "updated successfully" in response.json()["message"]

    def test_update_customer_not_found(self, client: TestClient):
        updated_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "address": "New Address",
        }
        response = client.put(f"/v1/customers/{uuid.uuid4()}", json=updated_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetAllCustomersEndpoint:
    def test_get_all_customers_empty(self, client: TestClient):
        response = client.get("/v1/customers/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_all_customers(self, client: TestClient, multiple_customers):
        response = client.get("/v1/customers/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5


class TestGetActiveCustomersEndpoint:
    def test_get_active_customers_empty(self, client: TestClient):
        response = client.get("/v1/customers/active")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_active_customers(self, client: TestClient, multiple_customers):
        response = client.get("/v1/customers/active")
        assert response.status_code == status.HTTP_200_OK
        active_count = sum(1 for c in multiple_customers if c.is_active)
        assert len(response.json()) == active_count


class TestGetCustomerByIdEndpoint:
    def test_get_customer_by_id_success(self, client: TestClient, sample_customer):
        response = client.get(f"/v1/customers/{sample_customer.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_customer.id)
        assert data["first_name"] == "John"

    def test_get_customer_by_id_not_found(self, client: TestClient):
        response = client.get(f"/v1/customers/{uuid.uuid4()}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteCustomerEndpoint:
    def test_delete_customer_success(self, client: TestClient, sample_customer):
        response = client.delete(f"/v1/customers/{sample_customer.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        verify_response = client.get(f"/v1/customers/{sample_customer.id}")
        assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_customer_not_found(self, client: TestClient):
        response = client.delete(f"/v1/customers/{uuid.uuid4()}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
