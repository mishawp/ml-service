import os
import pytest
from dotenv import load_dotenv
from fastapi import status
from httpx import AsyncClient
from sqlmodel import Session
from models import User
from services.crud import UserService
from auth.hash_password import HashPassword


@pytest.mark.asyncio
async def test_login_positive(client: AsyncClient, session: Session):
    load_dotenv()
    # Создаем тестового пользователя
    user_service = UserService(session)
    test_user = User(
        email="test@example.com",
        password=HashPassword.create_hash("hashedpassword"),
    )
    user_service.create_one(test_user)

    # Пытаемся войти с правильными данными
    response = await client.post(
        "/login",
        data={"username": "test@example.com", "password": "hashedpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_302_FOUND
    assert os.getenv("COOKIE_NAME") in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, session: Session):
    # Создаем тестового пользователя
    user_service = UserService(session)
    test_user = User(
        email="test@example.com",
        password=HashPassword.create_hash("password"),
    )
    user_service.create_one(test_user)

    # Пытаемся войти с неправильными данными
    response = await client.post(
        "/login",
        data={"username": "test@example.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_login_wrong_user(client: AsyncClient, session: Session):
    response = await client.post(
        "/login",
        data={"username": "test@example.com", "password": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_signup_positive(client: AsyncClient, session: Session):
    response = await client.post(
        "/signup",
        data={
            "username": "test@example.com",
            "password": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    user = UserService(session).read_by_email("test@example.com")

    assert user is not None
    assert response.status_code == status.HTTP_302_FOUND
    assert os.getenv("COOKIE_NAME") in response.cookies


@pytest.mark.asyncio
async def test_signup_invalid_email(client: AsyncClient, session: Session):
    response = await client.post(
        "/signup",
        data={
            "username": "testexample.com",
            "password": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    user = UserService(session).read_by_email("username")

    assert user is None
    assert response.status_code is status.HTTP_422_UNPROCESSABLE_ENTITY
    assert os.getenv("COOKIE_NAME") not in response.cookies
