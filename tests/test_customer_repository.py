"""Tests for customer repository."""

import pytest
from fastapi import HTTPException

from models import Customer
from repositories.customer_repository import (
    create_customer,
    delete_customer,
    get_active_customer,
    get_all_customer,
    get_customer_by_id,
    update_customer,
)
from schemas.schemas import Customer as CustomerSchema


class TestCreateCustomer:
    def test_create_customer(self, db_session, sample_customer_data):
        customer_schema = CustomerSchema(**sample_customer_data)
        result = create_customer(customer_schema, db_session)

        assert result.id is not None
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.address == "123 Main St"
        assert result.is_active is False

    def test_create_customer_persisted(self, db_session, sample_customer_data):
        customer_schema = CustomerSchema(**sample_customer_data)
        create_customer(customer_schema, db_session)

        customers = db_session.query(Customer).all()
        assert len(customers) == 1
        assert customers[0].first_name == "John"


class TestGetAllCustomer:
    def test_get_all_customers_empty(self, db_session):
        result = get_all_customer(db_session)
        assert result == []

    def test_get_all_customers(self, db_session, multiple_customers):
        result = get_all_customer(db_session)
        assert len(result) == 5

    def test_get_all_customers_returns_all(self, db_session, sample_customer):
        result = get_all_customer(db_session)
        assert len(result) == 1
        assert result[0].first_name == "John"


class TestGetActiveCustomer:
    def test_get_active_customers_empty(self, db_session):
        result = get_active_customer(db_session)
        assert result == []

    def test_get_active_customers(self, db_session, multiple_customers):
        result = get_active_customer(db_session)
        active_count = sum(1 for c in multiple_customers if c.is_active)
        assert len(result) == active_count

    def test_get_active_customers_none_active(self, db_session, sample_customer):
        result = get_active_customer(db_session)
        assert len(result) == 0


class TestUpdateCustomer:
    def test_update_customer_success(self, db_session, sample_customer):
        updated_data = CustomerSchema(
            first_name="Updated",
            last_name="Name",
            address="New Address",
        )
        result = update_customer(str(sample_customer.id), updated_data, db_session)

        assert "message" in result
        assert "updated successfully" in result["message"]

        db_session.refresh(sample_customer)
        assert sample_customer.first_name == "Updated"
        assert sample_customer.last_name == "Name"
        assert sample_customer.address == "New Address"

    def test_update_customer_not_found(self, db_session):
        updated_data = CustomerSchema(
            first_name="Updated",
            last_name="Name",
            address="New Address",
        )
        with pytest.raises(HTTPException) as exc_info:
            update_customer("non-existent-id", updated_data, db_session)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail


class TestGetCustomerById:
    def test_get_customer_by_id_success(self, db_session, sample_customer):
        result = get_customer_by_id(str(sample_customer.id), db_session)
        assert result.id == sample_customer.id
        assert result.first_name == "John"

    def test_get_customer_by_id_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            get_customer_by_id("non-existent-id", db_session)

        assert exc_info.value.status_code == 404
        assert "not available" in exc_info.value.detail


class TestDeleteCustomer:
    def test_delete_customer_success(self, db_session, sample_customer):
        result = delete_customer(str(sample_customer.id), db_session)

        assert "message" in result
        assert "deleted" in result["message"]

        customers = db_session.query(Customer).all()
        assert len(customers) == 0

    def test_delete_customer_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            delete_customer("non-existent-id", db_session)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail

    def test_delete_customer_verifies_deletion(self, db_session, sample_customer):
        customer_id = str(sample_customer.id)
        delete_customer(customer_id, db_session)

        result = db_session.query(Customer).filter(Customer.id == sample_customer.id).first()
        assert result is None
