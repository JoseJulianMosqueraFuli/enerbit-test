from sqlalchemy import func
from sqlalchemy.orm import Session
from models import WorkOrder, Customer
from datetime import datetime
from sqlalchemy import extract


def calculate_average_duration(db: Session):
    average_duration = (
        db.query(func.avg(WorkOrder.planned_date_end - WorkOrder.planned_date_begin))
        .filter(WorkOrder.status == "done")
        .scalar()
    )
    return average_duration


def order_frequency_per_customer(db: Session):
    return (
        db.query(Customer.id, func.count(WorkOrder.id))
        .join(WorkOrder, Customer.id == WorkOrder.customer_id)
        .group_by(Customer.id)
        .order_by(func.count(WorkOrder.id).desc())
        .all()
    )


def identify_customer_activity_periods(db: Session):
    # Group by month and count work orders
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


def count_active_customers(db: Session, start: datetime, end: datetime):
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
