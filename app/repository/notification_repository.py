from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def create(db: AsyncSession, notification: Notification) -> Notification:
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def get_by_id(db: AsyncSession, notification_id: int) -> Notification | None:
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    return result.scalar_one_or_none()


async def list_all(db: AsyncSession) -> list[Notification]:
    result = await db.execute(select(Notification))
    return list(result.scalars().all())
