import pytest
from aio_pika.abc import AbstractChannel
from datetime import datetime, time
from fastapi import status
from httpx import AsyncClient
from sqlmodel import Session
from services.crud import (
    UserService,
    ChatService,
    PredictionService,
    CostService,
)
from models import Cost, Chat


@pytest.mark.asyncio
async def test_create_chat(client: AsyncClient, session: Session):
    response = await client.post(
        "/signup",
        data={
            "username": "test@example.com",
            "password": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response = await client.get("/chat/new_chat")
    assert response.status_code == status.HTTP_302_FOUND
    chat_id = int(response.headers["location"].split("/")[-1])
    chat_service = ChatService(session)
    chat = chat_service.read_by_id(chat_id)
    assert chat is not None
    assert chat.user_id == 1


@pytest.mark.asyncio
async def test_predict_positive(
    client: AsyncClient, session: Session, channel: AbstractChannel
):
    await client.post(
        "/signup",
        data={
            "username": "test@example.com",
            "password": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    chat = ChatService(session).create_one(Chat(user_id=1))
    cost = CostService(session).create_one(
        Cost(timestamp=datetime.now(), prediction_cost=1)
    )

    await client.post(
        "/chat/prediction",
        json={"chat_id": chat.chat_id, "model_input": "Some test text"},
    )

    wrong_statuses = ["expired", "invalid", "negative balance", "undefined"]
    response = await client.get(
        "/chat/prediction/status", params={"chat_id": chat.chat_id}
    )
    response = response.json()
    while response["status"] != "completed":
        assert response["status"] not in wrong_statuses
        response = await client.get(
            "/prediction/status", params={"chat_id": chat.chat_id}
        )
        response = response.json()
    prediction_service = PredictionService(session)

    assert prediction_service.read_by_id(1) is not None


@pytest.mark.asyncio
async def test_predict_invalid(
    client: AsyncClient, session: Session, channel: AbstractChannel
):
    await client.post(
        "/signup",
        data={
            "username": "test@example.com",
            "password": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    chat = ChatService(session).create_one(Chat(user_id=1))
    cost = CostService(session).create_one(
        Cost(timestamp=datetime.now(), prediction_cost=1)
    )

    await client.post(
        "/chat/prediction",
        json={"chat_id": chat.chat_id, "model_input": "Текст инвалид"},
    )

    wrong_statuses = ["expired", "completed", "negative balance", "undefined"]
    response = await client.get(
        "/chat/prediction/status", params={"chat_id": chat.chat_id}
    )
    response = response.json()
    while response["status"] != "invalid":
        assert response["status"] not in wrong_statuses
        response = await client.get(
            "/prediction/status", params={"chat_id": chat.chat_id}
        )
        response = response.json()
    prediction_service = PredictionService(session)

    assert prediction_service.read_by_id(1) is None


@pytest.mark.asyncio
async def test_predict_negative(
    client: AsyncClient, session: Session, channel: AbstractChannel
):
    await client.post(
        "/signup",
        data={
            "username": "test@example.com",
            "password": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    user = UserService(session).read_by_id(1)
    user.balance = -1
    session.commit()
    chat = ChatService(session).create_one(Chat(user_id=1))
    cost = CostService(session).create_one(
        Cost(timestamp=datetime.now(), prediction_cost=1)
    )

    await client.post(
        "/chat/prediction",
        json={"chat_id": chat.chat_id, "model_input": "Some test text"},
    )

    wrong_statuses = ["expired", "invalid", "completed", "undefined"]
    response = await client.get(
        "/chat/prediction/status", params={"chat_id": chat.chat_id}
    )
    response = response.json()
    while response["status"] != "negative balance":
        assert response["status"] not in wrong_statuses
        response = await client.get(
            "/prediction/status", params={"chat_id": chat.chat_id}
        )
        response = response.json()
    prediction_service = PredictionService(session)

    assert prediction_service.read_by_id(1) is None
