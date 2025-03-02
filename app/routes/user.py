from fastapi import APIRouter, Request, Depends
from typing import Annotated
from decimal import Decimal
from database.database import SessionDep
from auth.authenticate import authenticate_cookie
from models import Payment
from services.crud import PaymentService, UserService


route = APIRouter(prefix="/user", tags=["User"])


@route.get("/")
async def user(
    request: Request,
    session: SessionDep,
    username: Annotated[str, Depends(authenticate_cookie)],
):
    return "..."


@route.post("/pay")
async def pay(
    amount: Decimal,
    session: SessionDep,
    username: Annotated[str, Depends(authenticate_cookie)],
):
    user_service = UserService(session)
    payment_service = PaymentService(session)
    user = user_service.read_by_email(username)
    payment = Payment(amount=amount, user_id=user.user_id)
    # пока без администратора
    payment_service.update_user_balance(user, payment)
    payment = payment_service.create_one(payment)

    return payment


@route.get("/payments")
async def show_payments(
    session: SessionDep,
    username: Annotated[str, Depends(authenticate_cookie)],
):
    user_service = UserService(session)
    payment_service = PaymentService(session)
    user = user_service.read_by_email(username)
    payments = payment_service.read_by_user_id(user.user_id)

    return payments
