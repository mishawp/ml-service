import re
from datetime import datetime
from sqlmodel import Session
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from dataclasses import dataclass, field
from typing import Any, ClassVar
from models import Prediction, User, Chat
from services import PredictionService


@dataclass(frozen=True)
class MLModelService:
    tokenizer: ClassVar[GPT2Tokenizer] = None
    model: ClassVar[GPT2LMHeadModel] = None
    model_id: ClassVar[str] = None
    session: Session

    @classmethod
    def init_model(cls) -> Any:
        cls.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

        cls.model = GPT2LMHeadModel.from_pretrained("gpt2").to("cuda")

        cls.model_id = "gpt2"  # пока так

    @classmethod
    def predict(cls, request: str) -> str:
        # Токенизация запроса
        input_ids = cls.tokenizer.encode(request, return_tensors="pt").to(
            "cuda"
        )

        attention_mask = (
            input_ids.ne(cls.tokenizer.eos_token_id).long().to("cuda")
        )
        output = cls.model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=80,
            num_return_sequences=1,
            temperature=0.7,  # Контроль случайности
            top_k=30,  # Ограничение выбора топ-k токенов
            top_p=0.85,  # Ограничение выбора токенов по cumulative probability
            do_sample=True,
            pad_token_id=cls.tokenizer.eos_token_id,
            repetition_penalty=1.5,  # Штраф за повторения
        )

        # Декодируем результат
        response = cls.tokenizer.decode(output[0], skip_special_tokens=True)
        return response

    def make_prediction(
        self,
        *,
        request: str,
        timestamp: datetime = datetime.now(),
        chat_id: int,
        cost_id: int,
    ) -> Prediction:
        # нужна ли проверка на существование в бд user_id и cost_id?
        # кажется ошибки от субд будет достаточно
        response = self.__validate(request)
        if self.__is_negative_balance(chat_id):
            response += "Negative balance"
        if not response:
            response = self.predict(request)

        return Prediction(
            timestamp=timestamp,
            request=request,
            response=response,
            chat_id=chat_id,
            cost_id=cost_id,
            model=self.model_id,
        )

    @staticmethod
    def __validate(request: str) -> str:
        limit = 50
        pattern = r'^[a-zA-Z0-9,?\'";:!\.\- ]+$'
        if not re.match(pattern, request):
            return (
                "Use only Latin characters, numbers, and punctuation marks.\n"
            )
        if len(request) > limit:
            return f"The text is too long ({len(request)} characters out of {limit})\n"
        return ""

    def __is_negative_balance(self, chat_id: int) -> bool:
        chat = self.session.get(Chat, chat_id)
        user = self.session.get(User, chat.user_id)
        return user.balance < 0
