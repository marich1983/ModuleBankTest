import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums import OperationOutboxStatus


class OperationOutbox(Base):
    __tablename__ = "operation_outbox"

    __table_args__ = (
        Index(
            "ix_operation_outbox_status",
            "status"),
        UniqueConstraint(
            "operation_id",
            name="uq_operation_dispatch_operation_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    operation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("operations.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[OperationOutboxStatus] = mapped_column(
        Enum(
            OperationOutboxStatus,
            name="operation_outbox_status",
        ),
        nullable=False,
        default=OperationOutboxStatus.PENDING,
    )

    retry_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    operation: Mapped["Operation"] = relationship(
        back_populates="outbox"
    )

