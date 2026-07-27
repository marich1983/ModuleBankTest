from sqlalchemy import select
from sqlalchemy.dialects.mssql.information_schema import sequences

from app.db.session import async_session_maker
from app.enums import OperationEventType, OperationOutboxStatus, OperationStatus
from app.models import Operation, OperationEvent, OperationOutbox
from app.services.operation_event import get_next_event_number


async def mark_operation_success(operation):
    async with async_session_maker() as session:
        async with session.begin():
            operation_out = await session.scalar(
                select(OperationOutbox)
                .where(
                    OperationOutbox.operation_id == operation.id
                )
            )
            operation_out.status = OperationOutboxStatus.DONE


            sequence_number = await get_next_event_number(
                session,
                operation.id
            )

            session.add(
                OperationEvent(
                    operation_id=operation.id,
                    type=OperationEventType.SENT_TO_PROVIDER,
                    sequence_number=sequence_number,
                    from_status=OperationStatus.PROCESSING,
                    to_status=OperationStatus.PROCESSING,
                    message='Successfully sent to provider'
                )
            )

async def mark_operation_retry(operation):
        async with async_session_maker() as session:
            async with session.begin():
                operation_out = await session.scalar(
                    select(OperationOutbox)
                    .where(
                        OperationOutbox.operation_id == operation.id
                    )
                )
                operation_out.status = OperationOutboxStatus.PENDING
                operation_out.retry_count += 1


async def mark_operation_failed(operation):
    async with async_session_maker() as session:
        async with session.begin():
            operation_out = await session.scalar(
                select(OperationOutbox)
                .where(
                    OperationOutbox.operation_id == operation.id
                )
            )
            operation_out.status = OperationOutboxStatus.FAILED

            sequence_number = await get_next_event_number(
                session,
                operation.id
            )

            session.add(
                OperationEvent(
                    operation_id=operation.id,
                    type=OperationEventType.SENT_TO_PROVIDER,
                    sequence_number=sequence_number,
                    from_status=OperationStatus.PROCESSING,
                    to_status=OperationStatus.PROCESSING,
                    message='Unsuccessful sending to provider'
                )
            )

