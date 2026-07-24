from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Operation, OperationEvent
from app.enums import OperationStatus, OperationEventType


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


    event = OperationEvent(
        operation_id=operation.id,
        sequence_number=1,
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