import logging
from datetime import datetime, timezone

from app.client.base import NotificationSender
from app.models.notification import Notification
from app.models.user import User

logger = logging.getLogger(__name__)

_SMS_MAX_LENGTH = 160


class SmsSender(NotificationSender):
    def send(self, notification: Notification, user: User) -> None:
        content = notification.content[:_SMS_MAX_LENGTH]
        sent_at = datetime.now(timezone.utc)

        # No hay un campo de telefono en el modelo User todavia, se
        # simula el registro del envio con el user.id como referencia.
        logger.info("SMS sent to user %s at %s: %s", user.id, sent_at.isoformat(), content)
