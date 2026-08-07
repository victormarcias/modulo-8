import logging
import re

from app.client.base import NotificationSender
from app.models.notification import Notification
from app.models.user import User

logger = logging.getLogger(__name__)

_EMAIL_REGEX_ = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmailSender(NotificationSender):
    def send(self, notification: Notification, user: User) -> None:
        if not _EMAIL_REGEX_.match(user.email):
            raise ValueError(f"Invalid email format: {user.email}")

        template = f"Subject: {notification.title}\n\n{notification.content}"

        logger.info("Email sent to %s: %s", user.email, template)
