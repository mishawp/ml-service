from fastapi import APIRouter, Request, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Annotated
from database.database import SessionDep
from auth.authenticate import authenticate_cookie
from models import Chat, Prediction
from services.crud import (
    ChatService,
    UserService,
    PredictionService,
    CostService,
    MLModelService,
)


route = APIRouter(prefix="/chat", tags=["Chat"])


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
):
    # html-ка будет возвращаться

    return username


@route.get("/{chat_id}")
async def open_chat(
    chat_id: int,
    session: SessionDep,
    username: Annotated[str, Depends(authenticate_cookie)],
):
    chat = get_user_chat(username, chat_id, session)
    prediction_service = PredictionService(session)
    predictions = prediction_service.read_by_chat_id(chat.chat_id)

    return predictions


@route.post("/make_prediction")
async def make_prediction(
    chat_id: int,
    model_input: str,
    session: SessionDep,
    username: Annotated[str, Depends(authenticate_cookie)],
):
    """Чего бы я хотел: Открыт чат. Пользователь вводит запрос. Производиться предикт и вставляется в html-ку. Не так, чтобы заново открывалась страница. Как это сделать - пока хз"""
    chat = get_user_chat(username, chat_id, session)

    mlmodel_service = MLModelService(session)
    prediction_service = PredictionService(session)
    prediction = mlmodel_service.make_prediction(
        request=model_input,
        chat_id=chat_id,
        cost_id=CostService.current_cost_id,
    )
    prediction = prediction_service.create_one(prediction)
    return prediction
