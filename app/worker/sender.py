import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.session import async_session_maker
from app.enums import (
    OperationEventType,
    OperationStatus,
)
from app.models import Operation, OperationEvent


from app.services.provider import send_to_provider


async def process_events():
    async with async_session_maker() as session:
        async with session.begin():
            result = await session.scalars(
                select(OperationEvent)
                .where(
                    OperationEvent.type == OperationEventType.REQUESTED,
                    OperationEvent.processed_at.is_(None),
                )
                .with_for_update(skip_locked=True)
                .limit(10)
            )

            events = result.all()

            now = datetime.now(timezone.utc)

            # for event in events:
            #     event.processed_at = now

    for event in events:
        try:
            await send_to_provider(event.operation_id)

            event.processed_at = now

            async with async_session_maker() as session:
                async with session.begin():
                    operation = await session.get(Operation, event.operation_id)

                    operation.status = OperationStatus.COMPLETED

                    session.add(
                        OperationEvent(
                            operation_id=operation.id,
                            type=OperationEventType.SENT_TO_PROVIDER,
                        )
                    )

                    session.add(
                        OperationEvent(
                            operation_id=operation.id,
                            type=OperationEventType.SUCCESS_FROM_PROVIDER,
                        )
                    )
        except Exception:

            async with async_session_maker() as session:
                async with session.begin():
                    operation = await session.get(Operation, event.operation_id)

                    operation.status = OperationStatus.FAILED

                    session.add(
                        OperationEvent(
                            operation_id=operation.id,
                            type=OperationEventType.FAIL_FROM_PROVIDER,
                        )
                    )


async def main():

    while True:
        await process_events()
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())