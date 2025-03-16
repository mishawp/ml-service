from fastapi import APIRouter, Request, Depends, Body
from fastapi.templating import Jinja2Templates
from typing import Annotated
from decimal import Decimal
from database.database import SessionDep
from auth.authenticate import authenticate_cookie
from models import Payment
from services.crud import (
    PaymentService,
    UserService,
    PredictionService,
    CostService,
)


templates = Jinja2Templates(directory="view")
route = APIRouter(prefix="/user", tags=["User"])


@route.get("/")
async def user(
    request: Request,
    session: SessionDep,
    username: Annotated[str, Depends(authenticate_cookie)],
):
    user_service = UserService(session)
    user = user_service.read_by_email(username)
    return templates.TemplateResponse(request, "user.html", {"user": user})


@route.post("/pay")
async def pay(
    amount: Annotated[Decimal, Body()],
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
    request: Request,
    session: SessionDep,
    username: Annotated[str, Depends(authenticate_cookie)],
):
    user_service = UserService(session)
    payment_service = PaymentService(session)
    prediction_service = PredictionService(session)
    cost_service = CostService(session)
    user = user_service.read_by_email(username)
    payments = payment_service.read_by_user_id(user.user_id)
    predictions = prediction_service.read_by_user_id(user.user_id)
    transactions = [
        {
            "timestamp": prediction.timestamp,
            "amount": -cost_service.read_by_id(
                prediction.cost_id
            ).prediction_cost,
            "operation": "Списание",
            "status": "Выполнено",
        }
        for prediction in predictions
    ] + [
        {
            "timestamp": payment.timestamp,
            "amount": payment.amount,
            "operation": "Зачисление",
            "status": "Выполнено" if payment.status else "Отклонено",
        }
        for payment in payments
    ]
    transactions.sort(key=lambda x: x["timestamp"], reverse=True)

    return templates.TemplateResponse(
        request, "payments.html", {"transactions": transactions}
    )
