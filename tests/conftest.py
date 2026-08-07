import os
from collections.abc import AsyncGenerator

import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.models import Base
from main import app

load_dotenv()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # beforeEach
    # engine nuevo por test: las conexiones de asyncpg quedan atadas al
    # event loop en el que se crean, y cada test corre en uno propio.
    engine = create_async_engine(os.environ["TEST_DATABASE_URL"])
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session
        # afterEach
        # limpia todas las tablas al terminar, para que cada test arranque en blanco
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()

    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
