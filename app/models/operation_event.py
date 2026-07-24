import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums import OperationEventType, OperationStatus


class OperationEvent(Base):
    __tablename__ = "operation_events"

    __table_args__ = (
        UniqueConstraint(
            "operation_id",
            "sequence_number",
            name="uq_operation_event_sequence",
        ),
        Index(
            "ix_operation_events_operation_id",
            "operation_id",
        ),
        Index(
            "ix_operation_events_created_at",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    operation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("operations.id"),
        nullable=False,
    )

    # Порядковый номер события внутри одной операции
    sequence_number: Mapped[int] = mapped_column(
        nullable=False,
    )

    type: Mapped[OperationEventType] = mapped_column(
        Enum(
            OperationEventType,
            name="operation_event_type",
        ),
        nullable=False,
    )

    from_status: Mapped[OperationStatus | None] = mapped_column(
        Enum(
            OperationStatus,
            name="operation_status",
            create_type=False,
        ),
        nullable=True,
    )

    to_status: Mapped[OperationStatus] = mapped_column(
        Enum(
            OperationStatus,
            name="operation_status",
            create_type=False,
        ),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    operation = relationship(
        "Operation",
        back_populates="events",
    )