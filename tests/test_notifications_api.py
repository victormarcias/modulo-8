import pytest
from httpx import AsyncClient


async def _register_and_login(
    client: AsyncClient, email: str = "pepe@mundo.com"
) -> tuple[int, dict[str, str]]:
    register_response = await client.post(
        "/users/",
        json={"username": "pepe", "email": email, "password": "password123"},
    )
    user_id = register_response.json()["id"]

    login_response = await client.post(
        "/auth/login",
        data={"username": email, "password": "password123"},
    )
    token = login_response.json()["access_token"]

    return user_id, {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_create_notification_success(client: AsyncClient):
    user_id, headers = await _register_and_login(client)

    response = await client.post(
        "/notifications/",
        json={"title": "Hola", "content": "Bienvenida", "channel": "email"},
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Hola"
    assert body["channel"] == "email"
    assert body["user_id"] == user_id


@pytest.mark.anyio
async def test_create_notification_requires_auth(client: AsyncClient):
    response = await client.post(
        "/notifications/",
        json={"title": "Hola", "content": "Bienvenida", "channel": "email"},
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_list_notifications(client: AsyncClient):
    _, headers = await _register_and_login(client)
    await client.post(
        "/notifications/",
        json={"title": "A", "content": "a", "channel": "email"},
        headers=headers,
    )
    await client.post(
        "/notifications/",
        json={"title": "B", "content": "b", "channel": "sms"},
        headers=headers,
    )

    response = await client.get("/notifications/", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


@pytest.mark.anyio
async def test_get_notification_not_found(client: AsyncClient):
    _, headers = await _register_and_login(client)

    response = await client.get("/notifications/99999", headers=headers)

    assert response.status_code == 404
