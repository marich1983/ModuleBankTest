from sqlalchemy import select

from app.db.session import async_session_maker
from app.enums import OperationEventType, OperationOutboxStatus, OperationStatus
from app.models import Operation, OperationOutbox
from app.services.operation_event import add_operation_event


async def mark_operation_success(operation_out: OperationOutbox):
    async with async_session_maker() as session:
        async with session.begin():
            operation_out = await session.scalar(
                select(OperationOutbox).where(
                    OperationOutbox.operation_id == operation_out.operation_id
                )
            )

            operation = await session.get(
                Operation,
                operation_out.operation_id,
            )
            operation_out.status = OperationOutboxStatus.DONE

            await add_operation_event(
                session=session,
                operation=operation,
                event_type=OperationEventType.SENT_TO_PROVIDER,
                from_status=OperationStatus.PROCESSING,
                to_status=OperationStatus.PROCESSING,
                message="Successfully sent to provider",
            )


async def mark_operation_retry(operation_out: OperationOutbox):
    async with async_session_maker() as session:
        async with session.begin():
            operation_out = await session.scalar(
                select(OperationOutbox).where(
                    OperationOutbox.operation_id == operation_out.operation_id
                )
            )

            operation_out.status = OperationOutboxStatus.PENDING
            operation_out.retry_count += 1


async def mark_outbox_failed(operation_out: OperationOutbox):
    async with async_session_maker() as session:
        async with session.begin():
            operation = await session.get(
                Operation,
                operation_out.operation_id,
            )

            operation_out = await session.scalar(
                select(OperationOutbox).where(
                    OperationOutbox.operation_id == operation_out.operation_id
                )
            )

            old_status = operation.status
            operation_out.status = OperationOutboxStatus.FAILED


            await add_operation_event(
                session=session,
                operation=operation,
                event_type=OperationEventType.SEND_FAILED,
                from_status=old_status,
                to_status=old_status,
                message="Provider unavailable",
            )
