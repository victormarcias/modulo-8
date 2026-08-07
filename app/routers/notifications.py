from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationRead, NotificationUpdate
from app.service import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/", response_model=NotificationRead, status_code=201)
async def create_notification(
    payload: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await notification_service.create_notification(db, payload, current_user)


@router.get("/", response_model=list[NotificationRead])
async def list_notifications(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await notification_service.list_notifications(db, current_user.id)


@router.get("/{notification_id}", response_model=NotificationRead)
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await notification_service.get_owned_notification(db, notification_id, current_user.id)


@router.put("/{notification_id}", response_model=NotificationRead)
async def update_notification(
    notification_id: int,
    payload: NotificationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await notification_service.update_notification(
        db, notification_id, payload, current_user.id
    )


@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await notification_service.delete_notification(db, notification_id, current_user.id)
