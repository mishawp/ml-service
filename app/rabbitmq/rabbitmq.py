import aio_pika
from aio_pika.abc import AbstractChannel
from fastapi import Depends
from typing import Annotated
from .config import get_rabbitmq_settings

settings = get_rabbitmq_settings()

connection = None


async def connect_rabbitmq():
    global connection
    connection = await aio_pika.connect(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        login=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASS,
    )


async def close_rabbitmq_connection():
    global connection
    await connection.close()


def get_connection():
    return connection


async def get_channel():
    async with connection.channel() as channel:
        yield channel


AsyncChannelDep = Annotated[AbstractChannel, Depends(get_channel)]
