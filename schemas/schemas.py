from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from typing import List
from enum import Enum
from datetime import datetime


import uuid


class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    address: str


class Customer(CustomerBase):
    class Config:
        from_attributes = True


class CustomerId(BaseModel):
    id: uuid.UUID

    @validator("id")
    def validate_uuid(cls, value):
        if not isinstance(value, uuid.UUID):
            try:
                value = uuid.UUID(value)
            except ValueError:
                raise ValueError("Invalid UUID format")
        return value


class StatusEnum(str, Enum):
    new = "new"
    done = "done"
    cancelled = "cancelled"


class WorkOrderBase(BaseModel):
    title: str
    planned_date_begin: datetime
    planned_date_end: datetime
    status: StatusEnum

    @validator("planned_date_end")
    def validate_time_difference(cls, planned_date_end, values):
        planned_date_begin = values.get("planned_date_begin")
        if planned_date_begin and planned_date_end:
            if planned_date_end <= planned_date_begin:
                raise ValueError("End time should be later than start time")
            time_difference = planned_date_end - planned_date_begin
            if time_difference < timedelta(hours=2):
                raise ValueError("Time difference should be at least 2 hours")
        return planned_date_end


class WorkOrder(WorkOrderBase):
    id: uuid.UUID
    customer_id: uuid.UUID

    @validator("customer_id")
    def validate_uuid(cls, value):
        if not isinstance(value, uuid.UUID):
            try:
                value = uuid.UUID(value)
            except ValueError:
                raise ValueError("Invalid UUID format")
        return value

    class Config:
        from_attributes = True


class ShowCustomer(CustomerBase):
    id: uuid.UUID
    start_date: datetime | None
    end_date: datetime | None
    is_active: bool
    created_at: datetime
    work_orders: List[WorkOrder]

    class Config:
        from_attributes = True


class ShowWorkOrder(WorkOrderBase):
    id: uuid.UUID
    owner: ShowCustomer

    class Config:
        from_attributes = True


class ShowCustomerWorkOrderList(ShowCustomer):
    work_orders: List[WorkOrder]

    class Config:
        from_attributes = True


def parse_datetime(date_string: str) -> datetime:
    """Converts a date string to a date and time object."""
    try:
        return datetime.fromisoformat(date_string)
    except ValueError:
        raise ValueError(
            "Invalid date and time format. Use ISO format (YYYYY-MM-DDTHH:MM:SS)"
        )
