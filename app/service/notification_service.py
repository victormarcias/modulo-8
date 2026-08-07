from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.client.registry import get_sender
from app.models.notification import Notification
from app.models.user import User
from app.repository import notification_repository
from app.schemas.notification import NotificationCreate, NotificationUpdate


async def create_notification(
    db: AsyncSession, payload: NotificationCreate, user: User
) -> Notification:
    notification = Notification(
        title=payload.title,
        content=payload.content,
        channel=payload.channel,
        user_id=user.id,
    )
    notification = await notification_repository.create(db, notification)

    sender = get_sender(notification.channel)
    sender.send(notification, user)

    return notification


async def get_owned_notification(
    db: AsyncSession, notification_id: int, user_id: int
) -> Notification:
    notification = await notification_repository.get_by_id(db, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return notification


async def list_notifications(db: AsyncSession, user_id: int) -> list[Notification]:
    return await notification_repository.list_by_user(db, user_id)


async def update_notification(
    db: AsyncSession, notification_id: int, payload: NotificationUpdate, user_id: int
) -> Notification:
    notification = await get_owned_notification(db, notification_id, user_id)

    if payload.title is not None:
        notification.title = payload.title
    if payload.content is not None:
        notification.content = payload.content
    if payload.channel is not None:
        notification.channel = payload.channel

    return await notification_repository.update(db, notification)


async def delete_notification(db: AsyncSession, notification_id: int, user_id: int) -> None:
    notification = await get_owned_notification(db, notification_id, user_id)
    await notification_repository.delete(db, notification)
