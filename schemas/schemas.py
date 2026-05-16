"""Pydantic schemas module.

This module defines all Pydantic models for request/response validation.
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    address: str


class Customer(CustomerBase):
    model_config = ConfigDict(from_attributes=True)


class CustomerId(BaseModel):
    id: uuid.UUID

    @field_validator("id")
    @classmethod
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

    @model_validator(mode="after")
    def validate_time_difference(self):
        if self.planned_date_begin and self.planned_date_end:
            if self.planned_date_end <= self.planned_date_begin:
                raise ValueError("End time should be later than start time")
            time_difference = self.planned_date_end - self.planned_date_begin
            if time_difference < timedelta(hours=2):
                raise ValueError("Time difference should be at least 2 hours")
        return self


class WorkOrder(WorkOrderBase):
    id: uuid.UUID
    customer_id: uuid.UUID

    @field_validator("customer_id")
    @classmethod
    def validate_uuid(cls, value):
        if not isinstance(value, uuid.UUID):
            try:
                value = uuid.UUID(value)
            except ValueError:
                raise ValueError("Invalid UUID format")
        return value

    model_config = ConfigDict(from_attributes=True)


class ShowCustomer(CustomerBase):
    id: uuid.UUID
    start_date: datetime | None
    end_date: datetime | None
    is_active: bool
    created_at: datetime
    work_orders: List[WorkOrder]

    model_config = ConfigDict(from_attributes=True)


class ShowWorkOrder(WorkOrderBase):
    id: uuid.UUID
    owner: ShowCustomer

    model_config = ConfigDict(from_attributes=True)


class ShowCustomerWorkOrderList(ShowCustomer):
    work_orders: List[WorkOrder]

    model_config = ConfigDict(from_attributes=True)


def parse_datetime(date_string: str) -> datetime:
    """Converts a date string to a date and time object."""
    try:
        return datetime.fromisoformat(date_string)
    except ValueError:
        raise ValueError(
            "Invalid date and time format. Use ISO format (YYYYY-MM-DDTHH:MM:SS)"
        )
