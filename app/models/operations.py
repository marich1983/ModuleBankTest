import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums import *


class Operation(Base):
    __tablename__ = "operations"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="check_operation_amount_positive",
        ),
        Index(
            "ix_operations_status",
            "status",
        ),
        Index(
            "ix_operations_provider",
            "provider",
        ),
        Index(
            "ix_operations_created_at",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    currency: Mapped[Currency] = mapped_column(
        Enum(
            Currency,
            name="currency",
        ),
        nullable=False,
        default=Currency.RUB,
    )

    status: Mapped[OperationStatus] = mapped_column(
        Enum(
            OperationStatus,
            name="operation_status",
        ),
        nullable=False,
        default=OperationStatus.CREATED,
    )

    provider: Mapped[OperationProvider] = mapped_column(
        Enum(
            OperationProvider,
            name="operation_provider",
        ),
        nullable=False,
        default=OperationProvider.PROVIDER_SIMULATOR,
    )

    provider_payment_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )