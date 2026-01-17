from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from database import get_db
from models import WorkOrder
from repositories import work_order_repository
from schemas import schemas

router = APIRouter(prefix="/v1/work_orders", tags=["Work Orders"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.ShowWorkOrder
)
def create(request: schemas.WorkOrder, is_active: bool, db: Session = Depends(get_db)):
    return work_order_repository.create(request, is_active, db)


@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED)
def update(id, request: schemas.WorkOrder, db: Session = Depends(get_db)):
    return work_order_repository.update(id, request, db)


@router.put("/{id}/status/done", status_code=status.HTTP_202_ACCEPTED)
def finish(id, db: Session = Depends(get_db)):
    return work_order_repository.finish(id, db)


@router.get("/", response_model=List[schemas.ShowWorkOrder])
def get_all(db: Session = Depends(get_db)):
    return work_order_repository.get_all(db)


@router.get("/status-or-date")
def get_orders_within_range_or_by_status(
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if since and until:
        return work_order_repository.get_all_from_range(since, until, db)

    if status:
        return work_order_repository.get_orders_by_status(status, db)

    return {
        "error": "Por favor, proporcione al menos 'since' y 'until' o 'status' para la consulta."
    }


@router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=schemas.ShowWorkOrder
)
def show(id, response: Response, db: Session = Depends(get_db)):
    order = db.query(WorkOrder).filter(WorkOrder.id == id).first()

    if not order:
        response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with the id {id} is not available",
        )

    return order


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def destroy(id, db: Session = Depends(get_db)):
    order = db.query(WorkOrder).filter(WorkOrder.id == id)

    if not order.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The order width id {id} not found",
        )

    order.delete(synchronize_session=False)
    db.commit()
    return {"message": f"The order {id} has been deleted sucessfully"}
