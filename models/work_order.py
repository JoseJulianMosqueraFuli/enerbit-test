import uuid

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from datetime import datetime
from database import Base


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    title = Column(String, nullable=False)
    planned_date_begin = Column(DateTime, nullable=True)
    planned_date_end = Column(DateTime, nullable=True)
    status = Column(Enum("new", "done", "cancelled", name="status_enum"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    owner = relationship("Customer", back_populates="work_orders")

    def __init__(
        self, id, customer_id, title, planned_date_begin, planned_date_end, status
    ):
        self.id = id
        self.customer_id = customer_id
        self.title = title
        self.planned_date_begin = planned_date_begin
        self.planned_date_end = planned_date_end
        self.status = status
