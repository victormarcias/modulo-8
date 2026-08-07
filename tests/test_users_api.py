import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository import user_repository
from app.service.security import verify_password


@pytest.mark.anyio
async def test_create_user_success(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={"username": "pepe", "email": "pepe@mundo.com", "password": "password123"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "pepe@mundo.com"
    assert "password" not in body


@pytest.mark.anyio
async def test_create_user_hashes_password(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        "/users/",
        json={"username": "pepe", "email": "pepe@mundo.com", "password": "password123"},
    )
    assert response.status_code == 201

    user = await user_repository.get_by_email(db_session, "pepe@mundo.com")
    assert user is not None
    assert user.password_hash != "password123"
    assert verify_password("password123", user.password_hash)


@pytest.mark.anyio
async def test_user_already_exists(client: AsyncClient):
    payload = {"username": "pepe", "email": "pepe@mundo.com", "password": "password123"}

    first = await client.post("/users/", json=payload)
    assert first.status_code == 201

    second = await client.post("/users/", json=payload)
    assert second.status_code == 409
