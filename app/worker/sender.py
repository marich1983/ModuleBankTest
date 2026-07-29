import asyncio
import random

from sqlalchemy import select

from app.db.session import async_session_maker
from app.enums import OperationOutboxStatus
from app.models import Operation, OperationOutbox
from app.services.operation_outbox import (
    mark_operation_retry,
    mark_operation_success,
    mark_outbox_failed,
)

from app.services.provider import ProviderClient, ProviderUnavailable

MAX_RETRIES = 3
BASE_DELAY = 5

provider_client = ProviderClient()


async def process_operation_outbox():
    outbox = []

    async with async_session_maker() as session:
        async with session.begin():
            result = await session.scalars(
                select(OperationOutbox)
                .where(
                    OperationOutbox.status.in_(
                        [
                            OperationOutboxStatus.PENDING,
                            OperationOutboxStatus.PROCESSING,
                        ]
                    ),
                    OperationOutbox.retry_count < MAX_RETRIES,
                )
                .with_for_update(skip_locked=True)
                .limit(10)
            )

            outbox = result.all()

            if not outbox:
                return

            for operation_out in outbox:
                operation_out.status = OperationOutboxStatus.PROCESSING

    for operation_out in outbox:

        for retry in range(MAX_RETRIES):
            try:
                async with async_session_maker() as session:
                    operation = await session.get(
                        Operation,
                        operation_out.operation_id,
                    )

                    response = await provider_client.create_payment(operation)

                async with async_session_maker() as session:
                    async with session.begin():
                        operation = await session.get(
                            Operation,
                            operation_out.operation_id,
                        )
                        operation.provider_payment_id = response["providerPaymentId"]
                        # print(response["providerPaymentId"])

                        await mark_operation_success(operation_out)

                break

            except ProviderUnavailable:
                if retry == MAX_RETRIES - 1:
                    await mark_outbox_failed(operation_out)
                    break

                await mark_operation_retry(operation_out)

                delay = min(BASE_DELAY * (2**retry), 300)
                delay *= random.uniform(0.8, 1.2) # jitter чтобы избежать одновременной отправки

                await asyncio.sleep(delay)

            except Exception:
                raise


async def main():

    while True:
        try:
            await process_operation_outbox()
        except Exception:
            import traceback

            traceback.print_exc()

        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
