from fastapi import HTTPException, status, Response
from sqlalchemy.orm import Session
from models import Customer
from schemas import schemas
import uuid


def create_customer(request: schemas.Customer, db: Session):
    new_customer_id = str(uuid.uuid4())

    new_customer = Customer(
        id=new_customer_id,
        first_name=request.first_name,
        last_name=request.last_name,
        address=request.address,
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


def get_all_customer(db: Session):
    customers = db.query(Customer).all()
    return customers


def get_active_customer(db: Session):
    customers = db.query(Customer).filter(Customer.is_active == True).all()
    return customers


def update_customer(id, request: schemas.Customer, db: Session):
    customer = db.query(Customer).filter(Customer.id == id)

    if not customer.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The customer width id {id} not found",
        )

    customer.update(
        {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "address": request.address,
        }
    )

    db.commit()

    return {"message": f"The customer was updated successfully"}


def get_customer_by_id(id, db: Session):
    customer = db.query(Customer).filter(Customer.id == id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with the id {id} is not available",
        )

    return customer


def delete_customer(id, db: Session):
    customer = db.query(Customer).filter(Customer.id == id)

    if not customer.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The customer width id {id} not found",
        )

    customer.delete(synchronize_session=False)
    db.commit()
    return {"message": f"The customer {id} has been deleted sucessfully"}
