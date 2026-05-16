"""Work order model module.

This module defines the WorkOrder SQLAlchemy model.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses String(36).
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
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


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID, primary_key=True, default=uuid.uuid4
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("customers.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    planned_date_begin: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    planned_date_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(
        Enum("new", "done", "cancelled", name="status_enum", create_type=False)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    owner: Mapped["Customer"] = relationship(
        "Customer", back_populates="work_orders", lazy="joined"
    )
