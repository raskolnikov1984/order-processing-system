import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_order(async_client: AsyncClient, order):
    response = await async_client.post('/create_order', json=order)
    assert response.status_code == 201
    assert response.json() == {"message": "successful"}
