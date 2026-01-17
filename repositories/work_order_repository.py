"""Work order repository module.

This module contains all database operations related to work orders.
"""

import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import Customer, WorkOrder
from schemas import schemas
from tasks import redis_client


def create(request: schemas.WorkOrder, is_active: bool, db: Session) -> WorkOrder:
    """Create a new work order in the database.

    Args:
        request: Work order data from request
        is_active: Whether the customer should be marked as active
        db: Database session

    Returns:
        WorkOrder: The created work order object
    """
    total_work_orders = (
        db.query(WorkOrder).filter(WorkOrder.customer_id == request.customer_id).count()
    )

    if total_work_orders > 0:
        customer = db.query(Customer).filter(Customer.id == request.customer_id)

        if customer.first().is_active and is_active is False:
            customer.update({"is_active": is_active, "end_date": datetime.now()})

    new_order = WorkOrder(
        customer_id=request.customer_id,
        title=request.title,
        planned_date_begin=request.planned_date_begin,
        planned_date_end=request.planned_date_end,
        status="new",
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


def get_all(db: Session) -> list:
    """Get all work orders from the database.

    Args:
        db: Database session

    Returns:
        list: List of all work orders
    """
    orders = db.query(WorkOrder).all()
    return orders


def get_all_from_range(since: datetime, until: datetime, db: Session) -> list:
    """Get work orders created within a date range.

    Args:
        since: Start date
        until: End date
        db: Database session

    Returns:
        list: List of work orders within the date range
    """
    filtered_orders = (
        db.query(WorkOrder).filter(WorkOrder.created_at.between(since, until)).all()
    )

    return filtered_orders


def get_orders_by_status(status: str, db: Session) -> list:
    """Get work orders by status.

    Args:
        status: Work order status
        db: Database session

    Returns:
        list: List of work orders with the specified status
    """
    by_status = db.query(WorkOrder).filter(WorkOrder.status == status).all()
    return by_status


def update(id: str, request: schemas.WorkOrder, db: Session) -> dict:
    """Update an existing work order.

    Args:
        id: Work order ID
        request: Updated work order data
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If work order not found
    """
    order = db.query(WorkOrder).filter(WorkOrder.id == id)

    if not order.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The order width id {id} not found",
        )

    order.update(
        {
            "title": request.title,
            "planned_date_begin": request.planned_date_begin,
            "planned_date_end": request.planned_date_end,
            "status": request.status,
        }
    )

    db.commit()

    return {"message": f"The order was updated successfully"}


def finish(id: str, db: Session) -> dict:
    """Mark a work order as done and update customer status.

    Args:
        id: Work order ID
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If work order not found
    """
    order = db.query(WorkOrder).filter(WorkOrder.id == id)

    if not order.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The order width id {id} not found",
        )

    total_ended_orders = (
        db.query(WorkOrder)
        .filter(
            WorkOrder.customer_id == order.first().customer_id,
            WorkOrder.status == "done",
        )
        .count()
    )

    if total_ended_orders == 0:
        customer = db.query(Customer).filter(Customer.id == order.first().customer_id)
        customer.update({"is_active": True, "start_date": datetime.now()})

    order.update({"status": "done"})

    db.commit()

    event_data = {
        "id": str(order.first().id),
        "customer_id": str(order.first().customer_id),
        "title": order.first().title,
        "planned_date_begin": str(order.first().planned_date_begin),
        "planned_date_end": str(order.first().planned_date_end),
        "status": str(order.first().status),
        "created_at": str(order.first().created_at),
    }

    event_id = redis_client.xadd("order-completion-stream", event_data)
    print(event_id)

    return {"message": f"The order was updated successfully"}


def show(id: str, db: Session) -> WorkOrder:
    """Get a work order by ID.

    Args:
        id: Work order ID
        db: Database session

    Returns:
        WorkOrder: The work order object

    Raises:
        HTTPException: If work order not found
    """
    order = db.query(WorkOrder).filter(WorkOrder.id == id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with the id {id} is not available",
        )

    return order


def destroy(id: str, db: Session) -> dict:
    """Delete a work order from the database.

    Args:
        id: Work order ID
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If work order not found
    """
    order = db.query(WorkOrder).filter(WorkOrder.id == id)

    if not order.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The order width id {id} not found",
        )

    order.delete(synchronize_session=False)
    db.commit()
    return {"message": f"The order {id} has been deleted sucessfully"}
