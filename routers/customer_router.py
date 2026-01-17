from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from repositories import customer_repository
from schemas import schemas

router = APIRouter(prefix="/v1/customers", tags=["Customers"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create(request: schemas.Customer, db: Session = Depends(get_db)) -> dict:
    return customer_repository.create_customer(request, db)


@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED)
def update(id: str, request: schemas.Customer, db: Session = Depends(get_db)) -> dict:
    return customer_repository.update_customer(id, request, db)


@router.get("/", response_model=List[schemas.ShowCustomerWorkOrderList])
def get_all(db: Session = Depends(get_db)) -> List:
    return customer_repository.get_all_customer(db)


@router.get("/active")
def get_active(db: Session = Depends(get_db)) -> List:
    return customer_repository.get_active_customer(db)


@router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=schemas.ShowCustomer
)
def show(id: str, db: Session = Depends(get_db)) -> dict:
    return customer_repository.get_customer_by_id(id, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(id: str, db: Session = Depends(get_db)) -> dict:
    return customer_repository.delete_customer(id, db)
