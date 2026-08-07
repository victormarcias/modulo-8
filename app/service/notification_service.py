from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.client.registry import get_sender
from app.models.notification import Notification
from app.repository import notification_repository, user_repository
from app.schemas.notification import NotificationCreate


async def create_notification(
    db: AsyncSession, payload: NotificationCreate, user_id: int
) -> Notification:
    user = await user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    notification = Notification(
        title=payload.title,
        content=payload.content,
        channel=payload.channel,
        user_id=user_id,
    )
    notification = await notification_repository.create(db, notification)

    sender = get_sender(notification.channel)
    sender.send(notification, user)

    return notification


async def get_notification(db: AsyncSession, notification_id: int) -> Notification:
    notification = await notification_repository.get_by_id(db, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


async def list_notifications(db: AsyncSession) -> list[Notification]:
    return await notification_repository.list_all(db)
