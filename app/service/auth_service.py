from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repository import user_repository
from app.schemas.auth import Token
from app.service.security import create_access_token, decode_access_token, verify_password


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    user = await user_repository.get_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="User doesn't exist or credentials are invalid")
    return user


async def login(db: AsyncSession, email: str, password: str) -> Token:
    user = await authenticate_user(db, email, password)
    access_token = create_access_token(user.id)
    return Token(access_token=access_token)


async def get_user_from_token(db: AsyncSession, token: str) -> User:
    try:
        user_id = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user
