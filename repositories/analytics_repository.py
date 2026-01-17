"""Analytics repository module.

This module contains all database operations related to analytics and reporting.
"""

from datetime import datetime
from typing import Any, List, Tuple

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from models import Customer, WorkOrder


def calculate_average_duration(db: Session) -> Any:
    """Calculate the average duration of completed work orders.

    Args:
        db: Database session

    Returns:
        Any: Average duration as a timedelta or None
    """
    average_duration = (
        db.query(func.avg(WorkOrder.planned_date_end - WorkOrder.planned_date_begin))
        .filter(WorkOrder.status == "done")
        .scalar()
    )
    return average_duration


def order_frequency_per_customer(db: Session) -> List[Tuple]:
    """Get the order frequency for each customer.

    Args:
        db: Database session

    Returns:
        List[Tuple]: List of tuples containing customer ID and order count
    """
    return (
        db.query(Customer.id, func.count(WorkOrder.id))
        .join(WorkOrder, Customer.id == WorkOrder.customer_id)
        .group_by(Customer.id)
        .order_by(func.count(WorkOrder.id).desc())
        .all()
    )


def identify_customer_activity_periods(db: Session) -> List[Tuple]:
    """Identify customer activity periods by year and month.

    Args:
        db: Database session

    Returns:
        List[Tuple]: List of tuples containing year, month, and total orders
    """
    results = (
        db.query(
            extract("year", WorkOrder.created_at).label("year"),
            extract("month", WorkOrder.created_at).label("month"),
            func.count(WorkOrder.id).label("total"),
        )
        .group_by(
            extract("year", WorkOrder.created_at),
            extract("month", WorkOrder.created_at),
        )
        .order_by("year", "month")
        .all()
    )

    return results


def count_active_customers(db: Session, start: datetime, end: datetime) -> int:
    """Count active customers within a date range.

    Args:
        db: Database session
        start: Start date
        end: End date

    Returns:
        int: Number of active customers
    """
    active_customer_count = (
        db.query(func.count(Customer.id))
        .filter(
            Customer.is_active == True,
            Customer.start_date >= start,
            Customer.start_date <= end,
        )
        .scalar()
    )
    return active_customer_count
