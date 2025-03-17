import aio_pika
import json
from sqlmodel import Session
from aio_pika.abc import AbstractChannel
from dataclasses import dataclass
from typing import ClassVar
from models import User, Chat, Prediction
from services.crud import CostService


@dataclass(slots=True)
class MLModelService:
    # отслеживание отправленных к модели задачам.
    # в словарь добавляется correlation_id: model_input
    # и удаляется после получения ответа из очереди responses
    shared_requests_queue: ClassVar[dict[str, str]] = {}
    requests_queue_name: ClassVar[str] = "requests"
    responses_queue_name: ClassVar[str] = "responses"
    channel: AbstractChannel
    username: str
    session: Session | None = None

    async def publish_ml_task(
        self,
        *,
        model_input: str,
        chat_id: int,
    ) -> None:
        # объявляем очереди запросов и ответов
        await self.channel.declare_queue(
            name=self.responses_queue_name, durable=True
        )
        await self.channel.declare_queue(
            name=self.requests_queue_name,
            durable=True,
            arguments={
                "x-message-ttl": 60000,  # срок существования
                "x-dead-letter-exchange": self.channel.default_exchange.name,
                "x-dead-letter-routing-key": self.responses_queue_name,
            },
        )
        correlation_id = self.username + str(chat_id)
        self.shared_requests_queue[correlation_id] = model_input
        if self.__is_negative_balance(chat_id):
            response = json.dumps(
                {
                    "status": "negative balance",
                    "response": "Negative balance",
                }
            )
            message = aio_pika.Message(
                response.encode(),
                correlation_id=correlation_id,
                reply_to=self.responses_queue_name,
            )
            await self.channel.default_exchange.publish(
                message, routing_key=self.responses_queue_name
            )
        else:
            request = json.dumps(
                {
                    "request": model_input,
                    "chat_id": chat_id,
                    "cost_id": CostService.current_cost_id,
                }
            )
            message = aio_pika.Message(
                request.encode(),
                correlation_id=correlation_id,
                reply_to=self.responses_queue_name,
            )
            await self.channel.default_exchange.publish(
                message, routing_key=self.requests_queue_name
            )

    async def receive_ml_task(self, *, chat_id) -> dict[str, str]:
        correlation_id = self.username + str(chat_id)
        responses_queue = await self.channel.declare_queue(
            name=self.responses_queue_name, durable=True
        )
        response_message = None
        async with responses_queue.iterator() as queue_iter:
            async for message in queue_iter:
                if message.correlation_id == correlation_id:
                    response_message = message
                    await message.ack()
                    break

        # еще необработан моделью
        if response_message is None:
            return {"status": "processing"}

        # истек ли у задачи время нахождения в очереди requests
        if message.headers and "x-death" in message.headers:
            x_death = response_message.headers["x-death"]
            for entry in x_death:
                if entry.get("reason") == "expired":
                    response_data = {
                        "status": "expired",
                        "response": "The server is busy",
                    }
            else:
                response_data = {
                    "status": "undefined",
                    "response": "The server is busy",
                }
        else:
            response_body = message.body.decode()
            response_data = json.loads(response_body)

        self.shared_requests_queue.pop(correlation_id)
        return response_data

    # just for utils/fill_db.py
    async def wait_ml_task(self) -> dict[str, str]:
        responses_queue = await self.channel.declare_queue(
            name=self.responses_queue_name, durable=True
        )
        # Получаем первое доступное сообщение из очереди
        try:
            response_message = await responses_queue.get()
            await response_message.ack()
        except Exception as e:
            # Если очередь пуста или произошла ошибка
            return False
        correlation_id = response_message.correlation_id
        self.shared_requests_queue.pop(correlation_id)
        return True

    def __is_negative_balance(self, chat_id: int) -> bool:
        chat = self.session.get(Chat, chat_id)
        user = self.session.get(User, chat.user_id)
        return user.balance < 0

    @classmethod
    def get_request(cls, correlation_id: str) -> str | None:
        return cls.shared_requests_queue.get(correlation_id, None)
