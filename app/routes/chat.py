from fastapi import (
    APIRouter,
    Request,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
)
from fastapi.responses import RedirectResponse
from typing import Annotated
from database.database import SessionDep
from rabbitmq.rabbitmq import AsyncChannelDep, get_connection
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
):
    # html-ка будет возвращаться

    return username


@route.get("/{chat_id}")
async def open_chat(
    chat_id: int,
    session: SessionDep,
    username: Annotated[str, Depends(authenticate_cookie)],
):
    prediction_service = PredictionService(session)
    chat = get_user_chat(username, chat_id, session)
    mlmodel_input = MLModelService.shared_requests_queue.get(
        get_correlation_id(username, chat_id), None
    )
    if mlmodel_input:
        async with get_connection().channel() as channel:
            mlmodel_service = MLModelService(channel, username)
            mlmodel_response = await mlmodel_service.receive_ml_task(
                chat_id=chat_id
            )

        if mlmodel_response["status"] == "completed":
            prediction = Prediction(
                request=mlmodel_input,
                response=mlmodel_response["model_out"],
                chat_id=chat_id,
                cost_id=CostService.current_cost_id,
                model=mlmodel_response["model_id"],
            )
            prediction_service.create_one(prediction)

    predictions = prediction_service.read_by_chat_id(chat.chat_id)

    return predictions


@route.post("/prediction")
async def make_prediction(
    chat_id: int,
    model_input: str,
    session: SessionDep,
    username: Annotated[str, Depends(authenticate_cookie)],
    channel: AsyncChannelDep,
):
    """Чего бы я хотел: Открыт чат. Пользователь вводит запрос. Производиться предикт и вставляется в html-ку. Не так, чтобы заново открывалась страница. Как это сделать - пока хз"""
    # нельзя отправлять ml-задачу, пока предыдущая задача не была получена
    if (
        get_correlation_id(username, chat_id)
        in MLModelService.shared_requests_queue
    ):
        return {
            "status": "not available",
            "description": "The previous request has not been completed yet",
        }

    mlmodel_service = MLModelService(channel, username, session)
    await mlmodel_service.publish_ml_task(
        model_input=model_input,
        chat_id=chat_id,
    )
    # prediction = prediction_service.create_one(prediction)
    return {"status": "processing"}
