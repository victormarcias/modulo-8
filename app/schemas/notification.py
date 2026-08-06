from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.notification import NotificationChannel


class NotificationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    channel: NotificationChannel


class NotificationRead(BaseModel):
    id: int
    title: str
    content: str
    channel: NotificationChannel
    user_id: int
    created_at: datetime


class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    channel: Optional[NotificationChannel] = None
