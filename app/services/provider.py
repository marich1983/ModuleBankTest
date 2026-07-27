import asyncio


async def send_to_provider(operation):
    print(f"Sending operation {operation.id}")

    # имитация внешнего HTTP
    await asyncio.sleep(2)

    return True