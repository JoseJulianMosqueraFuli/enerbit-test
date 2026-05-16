"""Tests for SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import inspect

from models import Customer, WorkOrder


class TestCustomerModel:
    def test_customer_creation(self, sample_customer):
        assert sample_customer.id is not None
        assert isinstance(sample_customer.id, uuid.UUID)
        assert sample_customer.first_name == "John"
        assert sample_customer.last_name == "Doe"
        assert sample_customer.address == "123 Main St"
        assert sample_customer.is_active is False

    def test_customer_default_is_active(self, db_session):
        customer = Customer(
            first_name="Test",
            last_name="User",
            address="Test Address",
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        assert customer.is_active is False

    def test_customer_active_can_be_set(self, db_session):
        customer = Customer(
            first_name="Test",
            last_name="User",
            address="Test Address",
            is_active=True,
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        assert customer.is_active is True

    def test_customer_table_name(self):
        assert Customer.__tablename__ == "customers"

    def test_customer_columns(self):
        inspector = inspect(Customer)
        columns = [col.key for col in inspector.columns]
        assert "id" in columns
        assert "first_name" in columns
        assert "last_name" in columns
        assert "address" in columns
        assert "start_date" in columns
        assert "end_date" in columns
        assert "is_active" in columns
        assert "created_at" in columns


class TestWorkOrderModel:
    def test_work_order_creation(self, sample_work_order):
        assert sample_work_order.id is not None
        assert isinstance(sample_work_order.id, uuid.UUID)
        assert sample_work_order.title == "Test Work Order"
        assert sample_work_order.status == "new"

    def test_work_order_table_name(self):
        assert WorkOrder.__tablename__ == "work_orders"

    def test_work_order_columns(self):
        inspector = inspect(WorkOrder)
        columns = [col.key for col in inspector.columns]
        assert "id" in columns
        assert "customer_id" in columns
        assert "title" in columns
        assert "planned_date_begin" in columns
        assert "planned_date_end" in columns
        assert "status" in columns
        assert "created_at" in columns

    def test_work_order_status_values(self, db_session, sample_customer):
        for status_val in ["new", "done", "cancelled"]:
            order = WorkOrder(
                customer_id=sample_customer.id,
                title=f"Order {status_val}",
                planned_date_begin=datetime.now(timezone.utc),
                planned_date_end=datetime.now(timezone.utc),
                status=status_val,
            )
            db_session.add(order)
            db_session.commit()
            db_session.refresh(order)
            assert order.status == status_val

    def test_work_order_foreign_key(self, sample_work_order, sample_customer):
        assert sample_work_order.customer_id == sample_customer.id
