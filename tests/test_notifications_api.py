from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.models.notification import Notification
from app.models.user import User
from app.repository import notification_repository, user_repository


def _make_notification(notification_id: int, channel: str) -> Notification:
    return Notification(
        id=notification_id,
        title="Hola",
        content="Bienvenida",
        channel=channel,
        user_id=1,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.anyio
async def test_create_notification_sends_via_client(client: AsyncClient):
    fake_user = User(id=1, username="pepe", email="pepe@mundo.com", password_hash="x")
    fake_sender = MagicMock()

    def fake_create(db, notification):
        notification.id = 1
        notification.created_at = datetime.now(timezone.utc)
        return notification

    with (
        patch.object(user_repository, "get_by_id", new=AsyncMock(return_value=fake_user)),
        patch.object(notification_repository, "create", new=AsyncMock(side_effect=fake_create)),
        patch("app.service.notification_service.get_sender", return_value=fake_sender),
    ):
        response = await client.post(
            "/notifications/?user_id=1",
            json={"title": "Hola", "content": "Bienvenida", "channel": "email"},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Hola"
    assert body["channel"] == "email"

    # el service tiene que haber usado el sender del canal pedido, una sola vez
    fake_sender.send.assert_called_once()
    sent_notification, sent_user = fake_sender.send.call_args.args
    assert sent_notification.channel == "email"
    assert sent_user is fake_user


@pytest.mark.anyio
async def test_create_notification_user_not_found(client: AsyncClient):
    with patch.object(user_repository, "get_by_id", new=AsyncMock(return_value=None)):
        response = await client.post(
            "/notifications/?user_id=999",
            json={"title": "Hola", "content": "Bienvenida", "channel": "email"},
        )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_list_notifications(client: AsyncClient):
    fake_notifications = [_make_notification(1, "email"), _make_notification(2, "sms")]

    with patch.object(
        notification_repository, "list_all", new=AsyncMock(return_value=fake_notifications)
    ):
        response = await client.get("/notifications/")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["channel"] == "email"
    assert body[1]["channel"] == "sms"


@pytest.mark.anyio
async def test_get_notification_not_found(client: AsyncClient):
    with patch.object(notification_repository, "get_by_id", new=AsyncMock(return_value=None)):
        response = await client.get("/notifications/999")

    assert response.status_code == 404
