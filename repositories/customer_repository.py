"""Customer repository module.

This module contains all database operations related to customers.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import Customer
from schemas import schemas


def create_customer(request: schemas.Customer, db: Session) -> Customer:
    """Create a new customer in the database.

    Args:
        request: Customer data from request
        db: Database session

    Returns:
        Customer: The created customer object
    """
    new_customer = Customer(
        first_name=request.first_name,
        last_name=request.last_name,
        address=request.address,
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


def get_all_customer(db: Session) -> list:
    """Get all customers from the database.

    Args:
        db: Database session

    Returns:
        list: List of all customers
    """
    customers = db.query(Customer).all()
    return customers


def get_active_customer(db: Session) -> list:
    """Get all active customers from the database.

    Args:
        db: Database session

    Returns:
        list: List of active customers
    """
    customers = db.query(Customer).filter(Customer.is_active == True).all()
    return customers


def update_customer(id: str, request: schemas.Customer, db: Session) -> dict:
    """Update an existing customer.

    Args:
        id: Customer ID
        request: Updated customer data
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If customer not found
    """
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


def get_customer_by_id(id: str, db: Session) -> Customer:
    """Get a customer by ID.

    Args:
        id: Customer ID
        db: Database session

    Returns:
        Customer: The customer object

    Raises:
        HTTPException: If customer not found
    """
    customer = db.query(Customer).filter(Customer.id == id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with the id {id} is not available",
        )

    return customer


def delete_customer(id: str, db: Session) -> dict:
    """Delete a customer from the database.

    Args:
        id: Customer ID
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If customer not found
    """
    customer = db.query(Customer).filter(Customer.id == id)

    if not customer.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The customer width id {id} not found",
        )

    customer.delete(synchronize_session=False)
    db.commit()
    return {"message": f"The customer {id} has been deleted sucessfully"}
