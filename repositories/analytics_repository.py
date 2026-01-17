from datetime import datetime
from typing import Any, List, Tuple

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from models import Customer, WorkOrder


def calculate_average_duration(db: Session) -> Any:
    average_duration = (
        db.query(func.avg(WorkOrder.planned_date_end - WorkOrder.planned_date_begin))
        .filter(WorkOrder.status == "done")
        .scalar()
    )
    return average_duration


def order_frequency_per_customer(db: Session) -> List[Tuple]:
    return (
        db.query(Customer.id, func.count(WorkOrder.id))
        .join(WorkOrder, Customer.id == WorkOrder.customer_id)
        .group_by(Customer.id)
        .order_by(func.count(WorkOrder.id).desc())
        .all()
    )


def identify_customer_activity_periods(db: Session) -> List[Tuple]:
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
