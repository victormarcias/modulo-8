from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repository import user_repository
from app.schemas.user import UserCreate
from app.service.security import hash_password


async def register_user(db: AsyncSession, payload: UserCreate) -> User:
    existing = await user_repository.get_by_email(db, payload.email)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    return await user_repository.create(db, user)


async def get_user(db: AsyncSession, user_id: int) -> User:
    user = await user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def list_users(db: AsyncSession) -> list[User]:
    return await user_repository.list_all(db)
