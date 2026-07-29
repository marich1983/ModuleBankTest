import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.session import get_session
from app.db.base import Base

from app.models import (
    Operation,
    OperationEvent,
    OperationOutbox,
)


TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/db_operation_test"
)


@pytest_asyncio.fixture(scope="function")
async def db_engine():

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
        connect_args={
            "ssl": False,
            "timeout": 10,
        },
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session_factory(db_engine):

    return async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(autouse=True)
async def override_session(db_session_factory):

    async def _override_get_session():
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session

    yield

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

