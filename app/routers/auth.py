from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import Token
from app.service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # OAuth2PasswordRequestForm usa "username", nuestro login es por email
    return await auth_service.login(db, form_data.username, form_data.password)
