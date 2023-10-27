from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from models import WorkOrder, Customer
from schemas import schemas
from tasks import redis_client
import uuid


def create(request: schemas.WorkOrder, is_active: bool, db: Session):
    new_order_id = str(uuid.uuid4())
    total_work_orders = (
        db.query(WorkOrder).filter(WorkOrder.customer_id == request.customer_id).count()
    )

    if total_work_orders > 0:
        customer = db.query(Customer).filter(Customer.id == request.customer_id)

        if customer.first().is_active and is_active == False:
            customer.update({"is_active": is_active, "end_date": datetime.now()})

    new_order = WorkOrder(
        id=new_order_id,
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


def get_all(db: Session):
    orders = db.query(WorkOrder).all()
    return orders


def get_all_from_range(since, until, db: Session):
    filtered_orders = (
        db.query(WorkOrder).filter(WorkOrder.created_at.between(since, until)).all()
    )

    return filtered_orders


def get_orders_by_status(status, db: Session):
    by_status = db.query(WorkOrder).filter(WorkOrder.status == status).all()
    return by_status


def update(id, request: schemas.WorkOrder, db: Session):
    order = db.query(WorkOrder).filter(WorkOrder.id == id)

    if not order.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The order width id {id} not found",
        )

    order.update(
        {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "address": request.address,
        }
    )

    db.commit()

    return {"message": f"The order was updated successfully"}


def finish(id, db: Session):
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


def show(id, db: Session):
    order = db.query(WorkOrder).filter(WorkOrder.id == id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with the id {id} is not available",
        )

    return order


def destroy(id, db: Session):
    order = db.query(WorkOrder).filter(WorkOrder.id == id)

    if not order.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The order width id {id} not found",
        )

    order.delete(synchronize_session=False)
    db.commit()
    return {"message": f"The order {id} has been deleted sucessfully"}
