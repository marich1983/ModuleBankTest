import asyncio
import httpx
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.session import async_session_maker
from app.enums import (
    OperationEventType,
    OperationStatus,
    OperationOutboxStatus
)
from app.models import Operation, OperationEvent, OperationOutbox
from app.services.operation_outbox import (
    mark_operation_failed,
    mark_operation_success,
    mark_operation_retry
)

from app.services.provider import ProviderClient

MAX_RETRIES = 3
BASE_DELAY = 5

provider_client = ProviderClient()

async def process_operation_outbox():
    async with async_session_maker() as session:
        async with session.begin():
            result = await session.scalars(
                select(OperationOutbox)
                .where(
                    OperationOutbox.status == OperationOutboxStatus.PENDING,
                    OperationOutbox.retry_count < MAX_RETRIES,
                )
                .with_for_update(skip_locked=True)
                .limit(10)
            )

            outbox = result.all()

            for operation_out in outbox:
                operation_out.status = OperationOutboxStatus.PROCESSING


    for operation_out in outbox:

        async with async_session_maker() as session:
            operation = await session.get(
                Operation,
                operation_out.operation_id,
            )
            for retry in range(MAX_RETRIES):
                try:
                    response = await provider_client.create_payment(operation)
                    operation.provider_payment_id = response["providerPaymentId"]
                    print(response["providerPaymentId"])

                    await session.commit()

                    await mark_operation_success(operation)

                    break

                except (httpx.TimeoutException, httpx.ConnectError):
                    await mark_operation_retry(operation)

                    if retry == MAX_RETRIES - 1:
                        await mark_operation_failed(operation)
                        break

                    delay = min(BASE_DELAY * (2 ** retry), 300)

                    await asyncio.sleep(delay)


async def main():

    # while True:
    for _ in range(4):
        await process_operation_outbox()
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())