from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from src.db.base import Base
from src.db.session import get_db
from src.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://crm_user:crm_password@db_test:5432/crm_test"


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = None
    session = None
    try:
        engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        session = AsyncSession(engine, expire_on_commit=False)
        yield session
    except Exception as e:
        print(f"ERROR in db_session fixture: {type(e).__name__}: {e}")
        raise
    finally:
        if session:
            await session.close()
        if engine:
            await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
