import pytest


@pytest.mark.asyncio
async def test_receipt_idempotency(client):

    operation_id = "test-receipt-idempotency"

    # создаём операцию
    response = await client.post(
        "/operations",
        json={
            "operation_id": operation_id,
            "amount": "100.00",
            "currency": "RUB",
            "description": "test",
        },
    )

    assert response.status_code == 201

    # отправляем в обработку
    response = await client.post(
        f"/operations/{operation_id}/submit"
    )

    assert response.status_code == 202


    # первый receipt
    receipt = {
        "operationId": operation_id,
        "providerPaymentId": "provider-payment-123",
        "result": "COMPLETED",
        "message": "success",
        "occurredAt": "2026-07-29T12:00:00Z",
    }

    response = await client.post(
        "/receipts",
        json=receipt,
    )

    assert response.status_code in (200, 201)


    # повтор того же receipt
    response = await client.post(
        "/receipts",
        json=receipt,
    )

    assert response.status_code == 204


    # проверяем состояние операции
    response = await client.get(
        f"/operations/{operation_id}"
    )

    assert response.status_code == 200

    operation = response.json()

    assert operation["status"] == "COMPLETED"

    events = await client.get(
        f"/operations/{operation_id}/events"
    )

    events = events.json()

    assert len(events) == 3

    assert [
               event["type"]
               for event in events
           ] == [
               "CREATED",
               "REQUESTED",
               "SUCCESS_FROM_PROVIDER",
           ]
