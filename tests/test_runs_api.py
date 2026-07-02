import uuid

from httpx import AsyncClient


async def test_get_existing_run(client: AsyncClient) -> None:
    create_response = await client.post("/v1/briefs/decode", json={"text": "A brief to fetch later"})
    run_id = create_response.json()["run_id"]

    response = await client.get(f"/v1/briefs/runs/{run_id}")
    assert response.status_code == 200
    assert response.json()["run_id"] == run_id


async def test_get_missing_run_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"/v1/briefs/runs/{uuid.uuid4()}")
    assert response.status_code == 404
