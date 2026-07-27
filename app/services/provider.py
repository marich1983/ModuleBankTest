import asyncio


async def send_to_provider(operation):
    print(f"Sending operation {operation.id}")

    # имитация внешнего HTTP
    await asyncio.sleep(2)

    return True

# async def send_to_provider(operation: Operation):
#
#     payload = {
#         "operationId": operation.operation_id,
#         "amount": str(operation.amount),
#         "currency": operation.currency.value,
#     }
#
#     headers = {
#         "Idempotency-Key": operation.operation_id,
#         "X-Correlation-ID": operation.operation_id,
#     }
#
#     response = await client.post(
#         f"{settings.provider_url}/payments",
#         json=payload,
#         headers=headers,
#     )
#
#     response.raise_for_status()
#
#     data = response.json()
#
#     return data["providerPaymentId"]