from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from typing import Annotated
from .config import get_settings

engine = create_engine(
    url=get_settings().DATABASE_URL_psycopg,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

async_engine = create_engine(
    url=get_settings().DATABASE_URL_psycopg,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

async_engine = create_async_engine(
    url=get_settings().DATABASE_URL_asyncpg,
    echo=False,
    pool_size=5,
    max_overflow=10,
)


def get_session():
    with Session(engine) as session:
        yield session


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
AsyncSessionDep = Annotated[Session, Depends(get_async_session)]


def init_db():
    with engine.connect() as connection:
        connection.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
        connection.execute(text('DROP TABLE IF EXISTS "admin" CASCADE'))
        connection.execute(text("DROP TABLE IF EXISTS payment CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS chat CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS cost CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS prediction CASCADE"))
        connection.commit()
    SQLModel.metadata.create_all(engine)
