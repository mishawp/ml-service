import aio_pika
import json
from datetime import datetime
from sqlmodel import Session
from aio_pika.abc import AbstractChannel
from dataclasses import dataclass
from typing import ClassVar
from models import Prediction, User, Chat


@dataclass(slots=True)
class MLModelService:
    requests_queue_name: ClassVar[str] = "requests"
    responses_queue_name: ClassVar[str] = "responses"
    session: Session
    channel: AbstractChannel
    username: str

    async def make_prediction(
        self,
        *,
        request: str,
        timestamp: datetime = datetime.now(),
        chat_id: int,
        cost_id: int,
    ) -> Prediction:
        if self.__is_negative_balance(chat_id):
            response = "Negative balance"
        else:
            message = aio_pika.Message(
                request.encode(),
                correlation_id=self.username,
                reply_to=self.responses_queue_name,
            )
            requests_queue = await self.channel.declare_queue(
                name=self.requests_queue_name, durable=True
            )
            responses_queue = await self.channel.declare_queue(
                name=self.responses_queue_name, durable=True
            )
            await self.channel.default_exchange.publish(
                message, routing_key=self.requests_queue_name
            )

            async with responses_queue.iterator() as queue_iter:
                async for response_message in queue_iter:
                    async with response_message.process():
                        if response_message.correlation_id == self.username:
                            response = response_message.body.decode()
                            response = json.loads(response)
                            break

        # await responses_queue.delete()

        return Prediction(
            timestamp=timestamp,
            request=request,
            response=response.get("response"),
            chat_id=chat_id,
            cost_id=cost_id,
            model=response.get("model_id"),
        )

    def __is_negative_balance(self, chat_id: int) -> bool:
        chat = self.session.get(Chat, chat_id)
        user = self.session.get(User, chat.user_id)
        return user.balance < 0
