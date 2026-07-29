import logging

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import OperationEventType, OperationStatus
from app.models import Operation
from app.schemas import ReceiptResponse
from app.services.operation import processing_status_to_done
from app.services.operation_event import add_operation_event

logger = logging.getLogger(__name__)


async def get_operation_by_receipt(
    session: AsyncSession,
    operation_id: str,
) -> Operation | None:

    stmt = (
        select(Operation)
        .where(Operation.operation_id == operation_id)
        .with_for_update()
    )

    result = await session.execute(stmt)

    return result.scalar_one_or_none()


def check_provider_payment_id(
    operation: Operation,
    provider_payment_id: str,
) -> bool:
    """
    True - первая квитанция
    False - providerPaymentId уже был
    """

    if operation.provider_payment_id is None:
        operation.provider_payment_id = provider_payment_id
        return True

    if operation.provider_payment_id != provider_payment_id:
        raise HTTPException(
            status_code=409,
            detail="providerPaymentId does not match",
        )

    return False


async def receipt_processing(session: AsyncSession, receipt: ReceiptResponse):

    operation = await get_operation_by_receipt(
        session,
        receipt.operationId,
    )

    if operation is None:
        raise HTTPException(
            status_code=404,
            detail="Operation not found",
        )

    check_provider_payment_id(
        operation,
        receipt.providerPaymentId,
    )

    logger.info(
        "receipt.received status=%s",
        receipt.result,
        extra={
            "operation_id": operation.operation_id,
            "provider_payment_id": receipt.providerPaymentId or "-",
            "attempt": "-",
        },
    )

    if receipt.result == "COMPLETED":
        if operation.status == OperationStatus.COMPLETED:
            await add_operation_event(
                session=session,
                operation=operation,
                event_type=OperationEventType.COMPLETED,
                from_status=operation.status,
                to_status=operation.status,
                message="Finish",
            )
            return 204

        if operation.status == OperationStatus.REJECTED:
            # Поздняя конфликтующая квитанция
            await add_operation_event(
                session=session,
                operation=operation,
                event_type=OperationEventType.IGNORED,
                from_status=operation.status,
                to_status=operation.status,
                message="Ignored late conflicting receipt",
            )

            return 204

        await processing_status_to_done(
            session=session, operation=operation, receipt=receipt
        )

        return 200

    if receipt.result == "REJECTED":
        # Поздняя конфликтующая квитанция
        if operation.status == OperationStatus.COMPLETED:
            await add_operation_event(
                session=session,
                operation=operation,
                event_type=OperationEventType.IGNORED,
                from_status=operation.status,
                to_status=operation.status,
                message="Ignored late conflicting receipt",
            )

            return 204

        # Повтор REJECTED
        if operation.status == OperationStatus.REJECTED:
            await add_operation_event(
                session=session,
                operation=operation,
                event_type=OperationEventType.FAIL_FROM_PROVIDER,
                from_status=operation.status,
                to_status=operation.status,
                message="Duplicate receipt",
            )

            return 204

        # Первый REJECTED
        old_status = operation.status
        operation.status = OperationStatus.REJECTED

        await add_operation_event(
            session=session,
            operation=operation,
            event_type=OperationEventType.FAIL_FROM_PROVIDER,
            from_status=old_status,
            to_status=OperationStatus.REJECTED,
            message=receipt.message,
        )

        return 200
