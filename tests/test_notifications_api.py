import pytest
from httpx import AsyncClient


async def _create_user(client: AsyncClient, email: str = "pepe@mundo.com") -> int:
    response = await client.post(
        "/users/",
        json={"username": "pepe", "email": email, "password": "password123"},
    )
    return response.json()["id"]


@pytest.mark.anyio
async def test_create_notification_success(client: AsyncClient):
    user_id = await _create_user(client)

    response = await client.post(
        f"/notifications/?user_id={user_id}",
        json={"title": "Hola", "content": "Bienvenida", "channel": "email"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Hola"
    assert body["channel"] == "email"
    assert body["user_id"] == user_id


@pytest.mark.anyio
async def test_create_notification_user_not_found(client: AsyncClient):
    response = await client.post(
        "/notifications/?user_id=99999",
        json={"title": "Hola", "content": "Bienvenida", "channel": "email"},
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_list_notifications(client: AsyncClient):
    user_id = await _create_user(client)
    await client.post(
        f"/notifications/?user_id={user_id}",
        json={"title": "A", "content": "a", "channel": "email"},
    )
    await client.post(
        f"/notifications/?user_id={user_id}",
        json={"title": "B", "content": "b", "channel": "sms"},
    )

    response = await client.get("/notifications/")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


@pytest.mark.anyio
async def test_get_notification_not_found(client: AsyncClient):
    response = await client.get("/notifications/99999")

    assert response.status_code == 404
