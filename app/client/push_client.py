import logging

from app.client.base import NotificationSender
from app.models.notification import Notification
from app.models.user import User

logger = logging.getLogger(__name__)


class PushSender(NotificationSender):
    def send(self, notification: Notification, user: User) -> None:
        # No hay un campo de device token en el modelo User todavia, se
        # simula uno derivado del user.id para poder validar el flujo.
        device_token = f"device-token-user-{user.id}"

        if not device_token:
            raise ValueError("Missing device token")

        payload = {"title": notification.title, "body": notification.content}

        logger.info("Push sent to %s with payload %s", device_token, payload)
