import pytest
import httpx


@pytest.mark.anyio
async def test_index(client: httpx.AsyncClient):
    response = await client.get("/")
    print(response)
    assert response.status_code == 200
