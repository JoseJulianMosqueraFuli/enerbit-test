"""Pytest configuration and shared fixtures."""

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Generator

os.environ["SKIP_DB_INIT"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ENVIRONMENT"] = "test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, String, Boolean, DateTime, TypeDecorator
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from database import get_db
from models import Customer, WorkOrder


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses String(32),
    storing as stringified hex values.
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""

    from database import Base

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database dependency."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    from main import app
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_customer_data() -> dict:
    """Sample customer data for tests."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "address": "123 Main St",
    }


@pytest.fixture
def sample_customer(db_session: Session, sample_customer_data: dict) -> Customer:
    """Create a sample customer in the database."""
    customer = Customer(**sample_customer_data)
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def sample_work_order_data(sample_customer: Customer) -> dict:
    """Sample work order data for tests."""
    now = datetime.now(timezone.utc)
    return {
        "customer_id": str(sample_customer.id),
        "title": "Test Work Order",
        "planned_date_begin": (now + timedelta(hours=2)).isoformat(),
        "planned_date_end": (now + timedelta(hours=5)).isoformat(),
        "status": "new",
    }


@pytest.fixture
def sample_work_order(
    db_session: Session, sample_customer: Customer, sample_work_order_data: dict
) -> WorkOrder:
    """Create a sample work order in the database."""
    work_order = WorkOrder(
        customer_id=sample_customer.id,
        title=sample_work_order_data["title"],
        planned_date_begin=datetime.fromisoformat(
            sample_work_order_data["planned_date_begin"]
        ),
        planned_date_end=datetime.fromisoformat(
            sample_work_order_data["planned_date_end"]
        ),
        status=sample_work_order_data["status"],
    )
    db_session.add(work_order)
    db_session.commit()
    db_session.refresh(work_order)
    return work_order


@pytest.fixture
def multiple_customers(db_session: Session) -> list:
    """Create multiple customers in the database."""
    customers = []
    for i in range(5):
        customer = Customer(
            first_name=f"FirstName{i}",
            last_name=f"LastName{i}",
            address=f"{i} Street",
            is_active=i % 2 == 0,
        )
        db_session.add(customer)
        customers.append(customer)
    db_session.commit()
    for customer in customers:
        db_session.refresh(customer)
    return customers


@pytest.fixture
def multiple_work_orders(
    db_session: Session, sample_customer: Customer
) -> list:
    """Create multiple work orders in the database."""
    orders = []
    now = datetime.now(timezone.utc)
    for i in range(3):
        order = WorkOrder(
            customer_id=sample_customer.id,
            title=f"Order {i}",
            planned_date_begin=now + timedelta(hours=2 + i),
            planned_date_end=now + timedelta(hours=5 + i),
            status="new" if i < 2 else "done",
        )
        db_session.add(order)
        orders.append(order)
    db_session.commit()
    for order in orders:
        db_session.refresh(order)
    return orders
