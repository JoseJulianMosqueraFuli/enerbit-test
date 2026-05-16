"""Tests for Pydantic schemas."""

import uuid
from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from schemas.schemas import (
    Customer,
    CustomerBase,
    CustomerId,
    ShowCustomer,
    ShowCustomerWorkOrderList,
    ShowWorkOrder,
    StatusEnum,
    WorkOrder,
    WorkOrderBase,
    parse_datetime,
)


class TestCustomerBase:
    def test_valid_customer_base(self):
        data = {"first_name": "John", "last_name": "Doe", "address": "123 Main St"}
        customer = CustomerBase(**data)
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert customer.address == "123 Main St"

    def test_customer_base_missing_fields(self):
        with pytest.raises(ValidationError):
            CustomerBase(first_name="John")

    def test_customer_base_empty_fields(self):
        customer = CustomerBase(first_name="", last_name="", address="")
        assert customer.first_name == ""


class TestCustomer:
    def test_valid_customer(self):
        data = {"first_name": "John", "last_name": "Doe", "address": "123 Main St"}
        customer = Customer(**data)
        assert customer.first_name == "John"

    def test_customer_from_orm(self, sample_customer):
        customer = Customer.model_validate(sample_customer)
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"


class TestCustomerId:
    def test_valid_uuid(self):
        test_uuid = uuid.uuid4()
        customer_id = CustomerId(id=test_uuid)
        assert customer_id.id == test_uuid

    def test_invalid_uuid_format(self):
        with pytest.raises(ValidationError):
            CustomerId(id="not-a-uuid")


class TestStatusEnum:
    def test_status_new(self):
        assert StatusEnum.new == "new"

    def test_status_done(self):
        assert StatusEnum.done == "done"

    def test_status_cancelled(self):
        assert StatusEnum.cancelled == "cancelled"

    def test_invalid_status(self):
        with pytest.raises(ValueError):
            StatusEnum("invalid")


class TestWorkOrderBase:
    def test_valid_work_order_base(self):
        now = datetime.utcnow()
        data = {
            "title": "Test Order",
            "planned_date_begin": now,
            "planned_date_end": now + timedelta(hours=3),
            "status": "new",
        }
        wo = WorkOrderBase(**data)
        assert wo.title == "Test Order"
        assert wo.status == StatusEnum.new

    def test_end_before_start_raises_error(self):
        now = datetime.utcnow()
        with pytest.raises(ValidationError) as exc_info:
            WorkOrderBase(
                title="Test",
                planned_date_begin=now + timedelta(hours=5),
                planned_date_end=now,
                status="new",
            )
        assert "End time should be later than start time" in str(exc_info.value)

    def test_time_difference_less_than_2_hours_raises_error(self):
        now = datetime.utcnow()
        with pytest.raises(ValidationError) as exc_info:
            WorkOrderBase(
                title="Test",
                planned_date_begin=now,
                planned_date_end=now + timedelta(hours=1),
                status="new",
            )
        assert "Time difference should be at least 2 hours" in str(exc_info.value)

    def test_time_difference_exactly_2_hours_is_valid(self):
        now = datetime.utcnow()
        wo = WorkOrderBase(
            title="Test",
            planned_date_begin=now,
            planned_date_end=now + timedelta(hours=2),
            status="new",
        )
        assert wo.planned_date_end == now + timedelta(hours=2)


class TestWorkOrder:
    def test_valid_work_order(self):
        now = datetime.utcnow()
        data = {
            "id": uuid.uuid4(),
            "customer_id": uuid.uuid4(),
            "title": "Test Order",
            "planned_date_begin": now,
            "planned_date_end": now + timedelta(hours=3),
            "status": "new",
        }
        wo = WorkOrder(**data)
        assert wo.title == "Test Order"


class TestShowCustomer:
    def test_show_customer(self, sample_customer):
        show = ShowCustomer.model_validate(sample_customer)
        assert show.id == sample_customer.id
        assert show.first_name == sample_customer.first_name
        assert show.is_active == sample_customer.is_active


class TestShowWorkOrder:
    def test_show_work_order(self, sample_work_order):
        show = ShowWorkOrder.model_validate(sample_work_order)
        assert show.id == sample_work_order.id
        assert show.title == sample_work_order.title


class TestParseDatetime:
    def test_valid_iso_format(self):
        result = parse_datetime("2024-01-15T10:30:00")
        assert result == datetime(2024, 1, 15, 10, 30, 0)

    def test_valid_iso_format_with_timezone(self):
        result = parse_datetime("2024-01-15T10:30:00+00:00")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_invalid_format_raises_error(self):
        with pytest.raises(ValueError) as exc_info:
            parse_datetime("not-a-date")
        assert "Invalid date and time format" in str(exc_info.value)

    def test_date_only_format_raises_error(self):
        result = parse_datetime("2024-01-15")
        assert result.year == 2024
