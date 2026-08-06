from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.service.security import verify_password


@pytest.mark.anyio
async def test_create_user_success(client: AsyncClient):
    def fake_create(db, user):
        user.id = 1
        return user

    with (
        patch("app.repository.user_repository.get_by_email", new=AsyncMock(return_value=None)),
        patch("app.repository.user_repository.create", new=AsyncMock(side_effect=fake_create)),
    ):
        response = await client.post(
            "/users/",
            json={"username": "pepe", "email": "pepe@mundo.com", "password": "password123"},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["email"] == "pepe@mundo.com"
    assert "password" not in body


@pytest.mark.anyio
async def test_create_user_hashes_password(client: AsyncClient):
    created_user = {}

    def fake_create(db, user):
        user.id = 1
        created_user["user"] = user
        return user

    with (
        patch("app.repository.user_repository.get_by_email", new=AsyncMock(return_value=None)),
        patch("app.repository.user_repository.create", new=AsyncMock(side_effect=fake_create)),
    ):
        response = await client.post(
            "/users/",
            json={"username": "pepe", "email": "pepe@mundo.com", "password": "password123"},
        )

    assert response.status_code == 201

    # el password nunca se guarda en texto plano, y el hash tiene que
    # poder verificarse contra el password original
    password_hash = created_user["user"].password_hash
    assert password_hash != "password123"
    assert verify_password("password123", password_hash)


@pytest.mark.anyio
async def test_user_already_exists(client: AsyncClient):
    def fake_create(db, user):
        user.id = 1
        user.email = "pepe@mundo.com"
        return user

    with (
        patch("app.repository.user_repository.get_by_email", new=AsyncMock(return_value=None)),
        patch("app.repository.user_repository.create", new=AsyncMock(side_effect=fake_create)),
    ):
        response = await client.post(
            "/users/",
            json={"username": "pepe", "email": "pepe@mundo.com", "password": "password123"},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["email"] == "pepe@mundo.com"

    # try again to create the same user
    with (
        patch("app.repository.user_repository.get_by_email", new=AsyncMock(return_value="pepe@mundo.com")),
    ):
        response = await client.post(
            "/users/",
            json={"username": "pepe", "email": "pepe@mundo.com", "password": "password123"},
        )

    assert response.status_code == 409
