from sqlalchemy import select

from app.db.session import async_session_maker
from app.enums import OperationEventType, OperationOutboxStatus, OperationStatus
from app.models import Operation, OperationOutbox
from app.services.operation_event import add_operation_event


async def mark_operation_success(operation: Operation):
    async with async_session_maker() as session:
        async with session.begin():
            operation_out = await session.scalar(
                select(OperationOutbox).where(
                    OperationOutbox.operation_id == operation.id
                )
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


async def mark_operation_retry(operation: Operation):
    async with async_session_maker() as session:
        async with session.begin():
            operation_out = await session.scalar(
                select(OperationOutbox).where(
                    OperationOutbox.operation_id == operation.id
                )
            )
            operation_out.status = OperationOutboxStatus.PENDING
            operation_out.retry_count += 1


async def mark_operation_failed(operation: Operation):
    async with async_session_maker() as session:
        async with session.begin():
            operation_out = await session.scalar(
                select(OperationOutbox).where(
                    OperationOutbox.operation_id == operation.id
                )
            )
            operation_out.status = OperationOutboxStatus.FAILED

            await add_operation_event(
                session=session,
                operation=operation,
                event_type=OperationEventType.SENT_TO_PROVIDER,
                from_status=OperationStatus.PROCESSING,
                to_status=OperationStatus.PROCESSING,
                message="Unsuccessful sending to provider",
            )
