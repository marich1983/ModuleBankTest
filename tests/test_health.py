import pytest


@pytest.mark.asyncio
async def test_app_starts(client):
    response = await client.get("/health")

    assert response.status_code == 200