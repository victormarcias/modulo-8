from fastapi import APIRouter
from app.schemas.notification import NotificationCreate, NotificationRead

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/", response_model=NotificationRead)
def create_notification(payload: NotificationCreate):
    ...