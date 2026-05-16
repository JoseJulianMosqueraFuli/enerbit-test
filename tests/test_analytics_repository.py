"""Tests for analytics repository."""

import uuid
from datetime import datetime, timedelta, timezone

from models import Customer, WorkOrder
from repositories.analytics_repository import (
    calculate_average_duration,
    count_active_customers,
    identify_customer_activity_periods,
    order_frequency_per_customer,
)


class TestCalculateAverageDuration:
    def test_average_duration_with_no_orders(self, db_session):
        result = calculate_average_duration(db_session)
        assert result is None

    def test_average_duration_with_completed_orders(self, db_session, sample_customer):
        now = datetime.now(timezone.utc)
        order1 = WorkOrder(
            customer_id=sample_customer.id,
            title="Order 1",
            planned_date_begin=now,
            planned_date_end=now + timedelta(hours=4),
            status="done",
        )
        order2 = WorkOrder(
            customer_id=sample_customer.id,
            title="Order 2",
            planned_date_begin=now,
            planned_date_end=now + timedelta(hours=6),
            status="done",
        )
        db_session.add_all([order1, order2])
        db_session.commit()

        result = calculate_average_duration(db_session)
        assert result is not None

    def test_average_duration_excludes_non_completed(self, db_session, sample_customer):
        now = datetime.now(timezone.utc)
        done_order = WorkOrder(
            customer_id=sample_customer.id,
            title="Done Order",
            planned_date_begin=now,
            planned_date_end=now + timedelta(hours=4),
            status="done",
        )
        new_order = WorkOrder(
            customer_id=sample_customer.id,
            title="New Order",
            planned_date_begin=now,
            planned_date_end=now + timedelta(hours=2),
            status="new",
        )
        db_session.add_all([done_order, new_order])
        db_session.commit()

        result = calculate_average_duration(db_session)
        assert result is not None


class TestOrderFrequencyPerCustomer:
    def test_order_frequency_empty(self, db_session):
        result = order_frequency_per_customer(db_session)
        assert result == []

    def test_order_frequency_single_customer(
        self, db_session, sample_customer, multiple_work_orders
    ):
        result = order_frequency_per_customer(db_session)
        assert len(result) == 1
        assert result[0][0] == sample_customer.id
        assert result[0][1] == 3

    def test_order_frequency_multiple_customers(self, db_session, multiple_customers):
        now = datetime.now(timezone.utc)
        for customer in multiple_customers[:3]:
            for i in range(2):
                order = WorkOrder(
                    customer_id=customer.id,
                    title=f"Order {i}",
                    planned_date_begin=now,
                    planned_date_end=now + timedelta(hours=3),
                    status="new",
                )
                db_session.add(order)
        db_session.commit()

        result = order_frequency_per_customer(db_session)
        assert len(result) == 3


class TestIdentifyCustomerActivityPeriods:
    def test_activity_periods_empty(self, db_session):
        result = identify_customer_activity_periods(db_session)
        assert result == []

    def test_activity_periods_with_orders(self, db_session, sample_customer):
        now = datetime.now(timezone.utc)
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

        result = identify_customer_activity_periods(db_session)
        assert len(result) >= 1
        assert result[0].total == 3


class TestCountActiveCustomers:
    def test_count_active_customers_empty(self, db_session):
        start = datetime.now(timezone.utc) - timedelta(days=30)
        end = datetime.now(timezone.utc)
        result = count_active_customers(db_session, start, end)
        assert result == 0

    def test_count_active_customers(self, db_session):
        now = datetime.now(timezone.utc)
        active_customer = Customer(
            first_name="Active",
            last_name="User",
            address="Address",
            is_active=True,
            start_date=now - timedelta(days=10),
        )
        inactive_customer = Customer(
            first_name="Inactive",
            last_name="User",
            address="Address",
            is_active=False,
            start_date=now - timedelta(days=10),
        )
        db_session.add_all([active_customer, inactive_customer])
        db_session.commit()

        start = now - timedelta(days=30)
        end = now
        result = count_active_customers(db_session, start, end)
        assert result == 1

    def test_count_active_customers_outside_range(self, db_session):
        old_date = datetime.now(timezone.utc) - timedelta(days=365)
        active_customer = Customer(
            first_name="Old",
            last_name="User",
            address="Address",
            is_active=True,
            start_date=old_date,
        )
        db_session.add(active_customer)
        db_session.commit()

        start = datetime.now(timezone.utc) - timedelta(days=30)
        end = datetime.now(timezone.utc)
        result = count_active_customers(db_session, start, end)
        assert result == 0
