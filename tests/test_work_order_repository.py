"""Tests for work order repository."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from models import Customer, WorkOrder
from repositories.work_order_repository import (
    create,
    destroy,
    finish,
    get_all,
    get_all_from_range,
    get_orders_by_status,
    show,
    update,
)
from schemas.schemas import WorkOrder as WorkOrderSchema


class TestCreateWorkOrder:
    def test_create_work_order(self, db_session, sample_customer, sample_work_order_data):
        wo_schema = WorkOrderSchema(**sample_work_order_data)
        result = create(wo_schema, is_active=True, db=db_session)

        assert result.id is not None
        assert result.title == "Test Work Order"
        assert result.status == "new"
        assert result.customer_id == sample_customer.id

    def test_create_work_order_activates_customer(
        self, db_session, sample_customer, sample_work_order_data
    ):
        wo_schema = WorkOrderSchema(**sample_work_order_data)
        create(wo_schema, is_active=True, db=db_session)

        db_session.refresh(sample_customer)
        assert sample_customer.is_active is True

    def test_create_work_order_deactivates_customer_when_appropriate(
        self, db_session, sample_customer, sample_work_order_data
    ):
        sample_customer.is_active = True
        sample_customer.end_date = None
        db_session.commit()

        wo_schema = WorkOrderSchema(**sample_work_order_data)
        create(wo_schema, is_active=False, db=db_session)

        db_session.refresh(sample_customer)
        assert sample_customer.is_active is False
        assert sample_customer.end_date is not None


class TestGetAllWorkOrders:
    def test_get_all_empty(self, db_session):
        result = get_all(db_session)
        assert result == []

    def test_get_all_work_orders(self, db_session, multiple_work_orders):
        result = get_all(db_session)
        assert len(result) == 3


class TestGetAllFromRange:
    def test_get_all_from_range(self, db_session, sample_customer):
        now = datetime.now(timezone.utc)
        orders = []
        for i in range(3):
            order = WorkOrder(
                customer_id=sample_customer.id,
                title=f"Order {i}",
                planned_date_begin=now + timedelta(days=i),
                planned_date_end=now + timedelta(days=i, hours=3),
                status="new",
            )
            db_session.add(order)
            orders.append(order)
        db_session.commit()

        since = now - timedelta(hours=1)
        until = now + timedelta(days=2)
        result = get_all_from_range(since, until, db_session)
        assert len(result) >= 1

    def test_get_all_from_range_no_results(self, db_session, sample_customer):
        now = datetime.now(timezone.utc)
        order = WorkOrder(
            customer_id=sample_customer.id,
            title="Order",
            planned_date_begin=now,
            planned_date_end=now + timedelta(hours=3),
            status="new",
        )
        db_session.add(order)
        db_session.commit()

        future_since = now + timedelta(days=30)
        future_until = now + timedelta(days=60)
        result = get_all_from_range(future_since, future_until, db_session)
        assert result == []


class TestGetOrdersByStatus:
    def test_get_orders_by_status_new(self, db_session, multiple_work_orders):
        result = get_orders_by_status("new", db_session)
        assert len(result) == 2

    def test_get_orders_by_status_done(self, db_session, multiple_work_orders):
        result = get_orders_by_status("done", db_session)
        assert len(result) == 1

    def test_get_orders_by_status_no_results(self, db_session, sample_customer):
        result = get_orders_by_status("cancelled", db_session)
        assert result == []


class TestUpdateWorkOrder:
    def test_update_work_order_success(self, db_session, sample_work_order):
        now = datetime.now(timezone.utc)
        updated_data = WorkOrderSchema(
            id=sample_work_order.id,
            customer_id=sample_work_order.customer_id,
            title="Updated Title",
            planned_date_begin=now,
            planned_date_end=now + timedelta(hours=3),
            status="done",
        )
        result = update(str(sample_work_order.id), updated_data, db_session)

        assert "message" in result
        assert "updated successfully" in result["message"]

        db_session.refresh(sample_work_order)
        assert sample_work_order.title == "Updated Title"
        assert sample_work_order.status == "done"

    def test_update_work_order_not_found(self, db_session):
        now = datetime.now(timezone.utc)
        updated_data = WorkOrderSchema(
            id=uuid.uuid4(),
            customer_id=uuid.uuid4(),
            title="Updated",
            planned_date_begin=now,
            planned_date_end=now + timedelta(hours=3),
            status="new",
        )
        with pytest.raises(HTTPException) as exc_info:
            update("non-existent-id", updated_data, db_session)

        assert exc_info.value.status_code == 404


class TestFinishWorkOrder:
    def test_finish_work_order(self, db_session, sample_work_order):
        result = finish(str(sample_work_order.id), db_session)

        assert "message" in result
        db_session.refresh(sample_work_order)
        assert sample_work_order.status == "done"

    def test_finish_work_order_activates_customer(
        self, db_session, sample_work_order, sample_customer
    ):
        finish(str(sample_work_order.id), db_session)

        db_session.refresh(sample_customer)
        assert sample_customer.is_active is True
        assert sample_customer.start_date is not None

    def test_finish_work_order_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            finish("non-existent-id", db_session)

        assert exc_info.value.status_code == 404


class TestShowWorkOrder:
    def test_show_work_order_success(self, db_session, sample_work_order):
        result = show(str(sample_work_order.id), db_session)
        assert result.id == sample_work_order.id
        assert result.title == sample_work_order.title

    def test_show_work_order_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            show("non-existent-id", db_session)

        assert exc_info.value.status_code == 404


class TestDestroyWorkOrder:
    def test_destroy_work_order_success(self, db_session, sample_work_order):
        result = destroy(str(sample_work_order.id), db_session)

        assert "message" in result
        assert "deleted" in result["message"]

        orders = db_session.query(WorkOrder).all()
        assert len(orders) == 0

    def test_destroy_work_order_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            destroy("non-existent-id", db_session)

        assert exc_info.value.status_code == 404
