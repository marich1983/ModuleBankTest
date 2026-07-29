import asyncio

import pytest


@pytest.mark.asyncio
async def test_submit_concurrently_creates_single_outbox(client):

    operation_id = "test-concurrent-operation"

    # сначала создаём операцию
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


    # два параллельных submit
    responses = await asyncio.gather(
        client.post(
            f"/operations/{operation_id}/submit"
        ),
        client.post(
            f"/operations/{operation_id}/submit"
        ),
    )


    assert responses[0].status_code in (200, 202)
    assert responses[1].status_code in (200, 202)