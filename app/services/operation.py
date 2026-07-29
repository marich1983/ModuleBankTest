import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import OperationStatus, OperationEventType, OperationOutboxStatus
from app.models import Operation
from app.models.operation_outbox import OperationOutbox
from app.schemas import ReceiptResponse
from app.services.operation_event import add_operation_event

logger = logging.getLogger(__name__)


async def create_operation(session: AsyncSession, data):
    result = await session.execute(
        select(Operation).where(Operation.operation_id == data.operationId)
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

    logger.info(
        "operation.created",
        extra={
            "operation_id": operation.operation_id,
        },
    )

    await add_operation_event(
        session=session,
        operation=operation,
        event_type=OperationEventType.CREATED,
        from_status=None,
        to_status=OperationStatus.CREATED,
        message="Operation created",
    )

    await session.commit()

    await session.refresh(operation)

    return operation


async def get_operation_by_operation_id(
    session: AsyncSession,
    operation_id: str,
) -> Operation | None:

    result = await session.execute(
        select(Operation).where(Operation.operation_id == operation_id)
    )

    return result.scalar_one_or_none()


from sqlalchemy import select


async def submit_operation_service(
    session: AsyncSession,
    operation_id: str,
):
    async with session.begin():
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
            return {"status_code": 200, "operation": operation}

        old_status = operation.status

        operation.status = OperationStatus.PROCESSING

        logger.info(
            "operation.submitted",
            extra={
                "operation_id": operation.operation_id,
                "provider_payment_id": operation.provider_payment_id or "-",
                "attempt": "-",
            },
        )

        await add_operation_event(
            session=session,
            operation=operation,
            event_type=OperationEventType.REQUESTED,
            from_status=old_status,
            to_status=OperationStatus.PROCESSING,
            message="Operation submitted for processing",
        )

        operation_outbox = OperationOutbox(
            operation_id=operation.id,
            status=OperationOutboxStatus.PENDING,
        )

        session.add(operation_outbox)

        await session.commit()

        return {"status_code": 202, "operation": operation}


async def processing_status_to_done(
    session: AsyncSession, operation: Operation, receipt: ReceiptResponse
):
    if operation.status == OperationStatus.PROCESSING:
        old_status = operation.status
        operation.status = OperationStatus.COMPLETED

        logger.info(
            "operation.completed",
            extra={
                "operation_id": operation.operation_id,
                "provider_payment_id": operation.provider_payment_id or "-",
                "attempt": "-",
            },
        )

        await add_operation_event(
            session=session,
            operation=operation,
            event_type=OperationEventType.SUCCESS_FROM_PROVIDER,
            from_status=old_status,
            to_status=OperationStatus.COMPLETED,
            message=receipt.message,
        )

    return operation
