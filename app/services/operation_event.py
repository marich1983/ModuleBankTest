from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import OperationEvent, Operation


async def get_next_event_number(
    session,
    operation_id
):
    result = await session.execute(
        select(
            func.max(OperationEvent.sequence_number)
        )
        .where(
            OperationEvent.operation_id == operation_id
        )
    )

    last = result.scalar()

    return (last or 0) + 1

async def get_operation_events(
    session: AsyncSession,
    id: UUID,
) -> list[OperationEvent]:

    result = await session.execute(
        select(OperationEvent)
        .where(
            OperationEvent.operation_id == id
        )
        .order_by(
            OperationEvent.sequence_number
        )
    )

    return list(result.scalars().all())

# async def get_all_events(
#         session: AsyncSession
# ):
#     result = await session.execute(
#         select(OperationEvent)
#     )
#
#     return list(result.scalars().all())