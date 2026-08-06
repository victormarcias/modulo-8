from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.notification import NotificationCreate, NotificationRead
from app.service import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


# TODO: user_id va como query param hasta que exista auth (JWT) y se
# pueda sacar del usuario autenticado en vez de pedirlo al cliente.
@router.post("/", response_model=NotificationRead, status_code=201)
async def create_notification(
    payload: NotificationCreate, user_id: int, db: AsyncSession = Depends(get_db)
):
    return await notification_service.create_notification(db, payload, user_id)


@router.get("/", response_model=list[NotificationRead])
async def list_notifications(db: AsyncSession = Depends(get_db)):
    return await notification_service.list_notifications(db)


@router.get("/{notification_id}", response_model=NotificationRead)
async def get_notification(notification_id: int, db: AsyncSession = Depends(get_db)):
    return await notification_service.get_notification(db, notification_id)
