from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Operation, OperationEvent, OperationOutbox
from app.enums import OperationStatus, OperationEventType, OperationOutboxStatus
from app.models.operation_outbox import OperationOutbox
from app.services.operation_event import get_next_event_number


async def create_operation(
    session: AsyncSession,
    data
):
    result = await session.execute(
        select(Operation)
        .where(
            Operation.operation_id == data.operationId
        )
    )

    existing = result.scalar_one_or_none()

    if existing:
        raise ValueError("Operation already exists")


    operation = Operation(
        operation_id=data.operationId,
        amount=data.amount,
        currency=data.currency,
        description=data.description,
        status=OperationStatus.CREATED,
    )

    session.add(operation)

    await session.flush()

    sequence_number = await get_next_event_number(
        session,
        operation.id
    )

    event = OperationEvent(
        operation_id=operation.id,
        sequence_number=sequence_number,
        type=OperationEventType.CREATED,
        from_status=None,
        to_status=OperationStatus.CREATED,
        message="Operation created",
    )

    session.add(event)

    await session.commit()

    await session.refresh(operation)

    return operation


async def get_operation_by_operation_id(
    session: AsyncSession,
    operation_id: str,
) -> Operation | None:

    result = await session.execute(
        select(Operation)
        .where(Operation.operation_id == operation_id)
    )

    return result.scalar_one_or_none()

from sqlalchemy import select, update, func


async def submit_operation_service(
    session: AsyncSession,
    operation_id: str,
):
    operation = await session.scalar(
        select(Operation)
        .where(Operation.operation_id == operation_id)
        .with_for_update()
    )

    if operation is None:
        raise HTTPException(
        status_code=404,
        detail="Operation not found",
    )


    if operation.status != OperationStatus.CREATED:
        raise HTTPException(
            status_code=409,
            detail="Operation cannot be submitted",
        )


    old_status = operation.status

    operation.status = OperationStatus.PROCESSING

    last_sequence = await session.scalar(
        select(func.max(OperationEvent.sequence_number))
        .where(
            OperationEvent.operation_id == operation.id
        )
    )

    next_sequence = (last_sequence or 0) + 1

    event = OperationEvent(
        operation_id=operation.id,
        sequence_number=next_sequence,
        type=OperationEventType.REQUESTED,
        from_status=old_status,
        to_status=OperationStatus.PROCESSING,
        message="Operation submitted for processing",
    )

    session.add(event)

    operation_outbox = OperationOutbox(
            operation_id=operation.id,
            status=OperationOutboxStatus.PENDING,
        )

    session.add(operation_outbox)


    await session.commit()

    return operation