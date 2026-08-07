from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def create(db: AsyncSession, notification: Notification) -> Notification:
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def get_by_id(db: AsyncSession, notification_id: int) -> Notification | None:
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    return result.scalar_one_or_none()


async def list_by_user(db: AsyncSession, user_id: int) -> list[Notification]:
    result = await db.execute(select(Notification).where(Notification.user_id == user_id))
    return list(result.scalars().all())


async def update(db: AsyncSession, notification: Notification) -> Notification:
    await db.commit()
    await db.refresh(notification)
    return notification


async def delete(db: AsyncSession, notification: Notification) -> None:
    await db.delete(notification)
    await db.commit()
