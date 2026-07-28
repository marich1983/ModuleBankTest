from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.enums import OperationEventType, OperationStatus
from app.models import OperationEvent, Operation


async def get_operation_events(
    session: AsyncSession,
    id: UUID,
) -> list[OperationEvent]:

    result = await session.execute(
        select(OperationEvent)
        .where(OperationEvent.operation_id == id)
        .order_by(OperationEvent.sequence_number)
    )

    return list(result.scalars().all())


async def add_operation_event(
    session: AsyncSession,
    operation: Operation,
    event_type: OperationEventType,
    from_status: OperationStatus | None,
    to_status: OperationStatus,
    message: str,
) -> None:
    last_sequence = await session.scalar(
        select(func.max(OperationEvent.sequence_number)).where(
            OperationEvent.operation_id == operation.id
        )
    )

    event = OperationEvent(
        operation_id=operation.id,
        sequence_number=(last_sequence or 0) + 1,
        type=event_type,
        from_status=from_status,
        to_status=to_status,
        message=message,
    )

    session.add(event)


# async def get_all_events(
#         session: AsyncSession
# ):
#     result = await session.execute(
#         select(OperationEvent)
#     )
#
#     return list(result.scalars().all())
