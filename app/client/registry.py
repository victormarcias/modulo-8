from app.client.base import NotificationSender
from app.client.email_client import EmailSender
from app.client.push_client import PushSender
from app.client.sms_client import SmsSender
from app.models.notification import NotificationChannel

_SENDERS: dict[NotificationChannel, NotificationSender] = {
    NotificationChannel.EMAIL: EmailSender(),
    NotificationChannel.SMS: SmsSender(),
    NotificationChannel.PUSH: PushSender(),
}


def get_sender(channel: NotificationChannel) -> NotificationSender:
    return _SENDERS[channel]
