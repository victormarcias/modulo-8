from abc import ABC, abstractmethod

from app.models.notification import Notification
from app.models.user import User


class NotificationSender(ABC):
    @abstractmethod
    def send(self, notification: Notification, user: User) -> None:
        ...
