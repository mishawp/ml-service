import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel import Session
from services.crud import ChatService


@pytest.mark.asyncio
async def test_create_chat(client: AsyncClient, session: Session):
    # Предположим, что у нас есть пользователь с email "test@example.com"
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
    # Предположим, что user_id = 1 для "test@example.com"
    assert chat.user_id == 1


# я не могу проверить работу consumer и rabbitmq, потому что
# consumer записывает prediction прямо в рабочую базу данных postgres;
