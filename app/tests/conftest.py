import pytest
import pytest_asyncio
import httpx
import aio_pika
import os
from dotenv import load_dotenv
from aio_pika.abc import AbstractChannel
from sqlmodel import Session, SQLModel, create_engine, text
from sqlmodel.pool import StaticPool

from main import app
from database.config import get_db_settings
from database.database import get_session
from rabbitmq.rabbitmq import get_channel


@pytest.fixture(name="session")
def session_fixture():
    settings = get_db_settings()
    engine = create_engine(settings.DATABASE_URL_test, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    with engine.connect() as connection:
        connection.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
        connection.execute(text('DROP TABLE IF EXISTS "admin" CASCADE'))
        connection.execute(text("DROP TABLE IF EXISTS payment CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS chat CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS cost CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS prediction CASCADE"))
        connection.commit()


@pytest_asyncio.fixture(name="channel")
async def channel_fixture():
    load_dotenv()
    connection = await aio_pika.connect(
        host="localhost",
        port=int(os.getenv("RABBITMQ_PORT", 5672)),
        login=os.getenv("RABBITMQ_USER"),
        password=os.getenv("RABBITMQ_PASS"),
    )

    async with connection.channel() as channel:
        yield channel

    await connection.close()


@pytest_asyncio.fixture(name="client")
async def client_fixture(session: Session, channel: AbstractChannel):
    def get_session_override():
        yield session

    async def get_channel_override():
        yield channel

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_channel] = get_channel_override
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        yield client
    app.dependency_overrides.clear()
