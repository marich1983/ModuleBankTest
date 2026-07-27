import asyncio
import httpx

from app.core.config import settings
from app.models import Operation


class ProviderError(Exception):
    pass


class ProviderUnavailable(ProviderError):
    pass


class ProviderClient:

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=5.0
        )

    async def create_payment(
        self,
        operation: Operation
    ) -> dict:

        payload = {
            "operationId": operation.operation_id,
            "amount": str(operation.amount),
            "currency": operation.currency.value
            ,
        }

        headers = {
            "Idempotency-Key": operation.operation_id,
            "X-Correlation-ID": operation.operation_id,
        }

        try:
            response = await self.client.post(
                f"{settings.PROVIDER_URL}/payments",
                json=payload,
                headers=headers,
            )

        except httpx.RequestError as e:
            raise ProviderUnavailable(
                f"network error: {e}"
            )

        if response.status_code == 503:
            raise ProviderUnavailable(
                "provider unavailable"
            )

        response.raise_for_status()
        print(response.json()["providerPaymentId"])

        return response.json()

