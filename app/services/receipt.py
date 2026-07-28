from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models import Operation


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
