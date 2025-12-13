import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_order(async_client: AsyncClient):
    response = await async_client.post('/create_order')

    assert response.status_code == 200
    assert response.json() == {"message": "successful"}
