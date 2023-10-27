import uuid

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from datetime import datetime
from database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    work_orders = relationship("WorkOrder", back_populates="owner")

    def __init__(
        self,
        id,
        first_name,
        last_name,
        address,
        start_date=None,
        end_date=None,
        is_active=False,
    ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active
