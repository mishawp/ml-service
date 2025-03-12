import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel import Session
from services.crud import PaymentService, UserService


@pytest.mark.asyncio
async def test_pay_positive(client: AsyncClient, session: Session):
    response = await client.post(
        "/signup",
        data={
            "username": "test@example.com",
            "password": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    amount = 100.0
    response = await client.post(f"/user/pay", json=float(amount))
    user = UserService(session).read_by_email("test@example.com")
    user_balance_before = float(user.balance)

    assert response.status_code == status.HTTP_200_OK
    session.refresh(user)
    payment_service = PaymentService(session)
    payments = payment_service.read_by_user_id(1)
    assert len(payments) == 1
    assert (
        float(payments[0].amount) + user_balance_before
        >= float(user.balance) - 0.0000001
    )


@pytest.mark.asyncio
async def test_show_payments(client: AsyncClient, session: Session):
    response = await client.post(
        "/signup",
        data={
            "username": "test@example.com",
            "password": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    amount = 100.0
    for i in range(10):
        response = await client.post("/user/pay", json=amount + i)
    response = await client.get("/user/payments")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]
    content = response.text
    assert all(
        True
        for amount in [100.0 + i for i in range(10)]
        if str(amount) in content
    )
