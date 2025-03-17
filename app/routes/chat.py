from fastapi import APIRouter, Request, Depends, HTTPException, status, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from database.database import SessionDep
from rabbitmq.rabbitmq import AsyncChannelDep
from auth.authenticate import authenticate_cookie
from models import Chat, Prediction
from services.crud import (
    ChatService,
    UserService,
    PredictionService,
    CostService,
    MLModelService,
)

templates = Jinja2Templates(directory="view")
route = APIRouter(prefix="/chat", tags=["Chat"])


def get_correlation_id(username: str, chat_id: int) -> str:
    return username + str(chat_id)


def get_user_chat(username: str, chat_id: int, session: SessionDep):
    user_service = UserService(session)
    chat_service = ChatService(session)
    user = user_service.read_by_email(username)
    chat = chat_service.read_user_chat(chat_id, user.user_id)
    if chat == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return chat


@route.get("/")
async def chats(
    request: Request,
    session: SessionDep,
    username: Annotated[str, Depends(authenticate_cookie)],
) -> HTMLResponse:
    user_service = UserService(session)
    chat_service = ChatService(session)
    user = user_service.read_by_email(username)
    chats = chat_service.read_by_user_id(user.user_id)
    return templates.TemplateResponse(request, "chats.html", {"chats": chats})


@route.get("/new_chat")
async def create_chat(
    request: Request,
    session: SessionDep,
    username: Annotated[str, Depends(authenticate_cookie)],
):
    user_service = UserService(session)
    chat_service = ChatService(session)
    user = user_service.read_by_email(username)
    new_chat = Chat(user_id=user.user_id)
    chat_service.create_one(new_chat)
    # Сидит рядом с мамой
    response = RedirectResponse(
        f"/chat/{new_chat.chat_id}", status.HTTP_302_FOUND
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@route.get("/{chat_id}")
async def open_chat(
    request: Request,
    chat_id: int,
    session: SessionDep,
    username: Annotated[str, Depends(authenticate_cookie)],
):
    prediction_service = PredictionService(session)
    cost_service = CostService(session)
    chat = get_user_chat(username, chat_id, session)
    predictions = prediction_service.read_by_chat_id(chat.chat_id)
    predictions = [pred.__dict__ for pred in predictions]
    for pred in predictions:
        pred["cost"] = cost_service.read_by_id(pred["cost_id"]).prediction_cost

    return templates.TemplateResponse(
        request,
        "chat.html",
        {
            "predictions": predictions,
        },
    )


@route.post("/prediction")
async def make_prediction(
    chat_id: Annotated[int, Body()],
    model_input: Annotated[str, Body()],
    username: Annotated[str, Depends(authenticate_cookie)],
    session: SessionDep,
    channel: AsyncChannelDep,
) -> dict:
    # нельзя отправлять ml-задачу, пока предыдущая задача не была получена
    if MLModelService.get_request(get_correlation_id(username, chat_id)):
        return {
            "status": "not available",
            "description": "The previous request has not been completed yet",
        }
    else:
        mlmodel_service = MLModelService(channel, username, session)
        await mlmodel_service.publish_ml_task(
            model_input=model_input,
            chat_id=chat_id,
        )
        return {
            "status": "processing",
            "description": "the request is being processed",
        }


@route.get("/prediction/status")
async def check_prediction_status(
    chat_id: int,
    username: Annotated[str, Depends(authenticate_cookie)],
    session: SessionDep,
    channel: AsyncChannelDep,
):
    correlation_id = get_correlation_id(username, chat_id)
    mlmodel_service = MLModelService(channel, username)
    if mlmodel_input := MLModelService.get_request(correlation_id):
        mlmodel_response = await mlmodel_service.receive_ml_task(
            chat_id=chat_id
        )
        if mlmodel_response["status"] == "completed":
            prediction_service = PredictionService(session)
            cost_service = CostService(session)
            prediction = prediction_service.read_by_id(
                mlmodel_response["response"]
            )
            cost = cost_service.read_by_id(prediction.cost_id)
            return {
                "status": "completed",
                "response": prediction.response,
                "cost": cost.prediction_cost,
            }
        elif mlmodel_response["status"] == "invalid":
            return {
                "status": "invalid",
                "response": mlmodel_response["response"],
            }
        elif mlmodel_response["status"] == "expired":
            return {"status": "expired", "response": "Server is busy"}
        elif mlmodel_response["status"] == "negative balance":
            return {
                "status": "negative balance",
                "response": "Negative balance",
            }
        elif mlmodel_response["status"] == "undefined":
            return {
                "status": "undefined",
                "response": "undefined error",
            }
    else:
        return {"status": "processing", "response": "processing"}
