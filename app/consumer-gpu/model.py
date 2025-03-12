import asyncio
import aio_pika
import re
import json
from sqlmodel import create_engine, Session
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from database.config import get_db_settings
from rabbitmq.config import get_rabbitmq_settings
from models import Prediction
from services.crud import PredictionService


tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

model = GPT2LMHeadModel.from_pretrained("gpt2").to("cuda")


def validate(model_input: str) -> str:
    limit = 50
    pattern = r'^[a-zA-Z0-9,?\'";:!\.\- ]+$'
    if not re.match(pattern, model_input):
        return "Use only Latin characters, numbers, and punctuation marks.\n"
    if len(model_input) > limit:
        return f"The text is too long ({len(model_input)} characters out of {limit})\n"
    return ""


def predict(model_input: str) -> str:
    # Токенизация запроса
    input_ids = tokenizer.encode(model_input, return_tensors="pt").to("cuda")

    attention_mask = input_ids.ne(tokenizer.eos_token_id).long().to("cuda")
    output = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_length=80,
        num_return_sequences=1,
        temperature=0.7,
        top_k=30,
        top_p=0.85,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        repetition_penalty=1.5,
    )

    # Декодируем результат
    model_out = tokenizer.decode(output[0], skip_special_tokens=True)
    return model_out


async def process_message(
    message: aio_pika.abc.AbstractIncomingMessage,
    channel: aio_pika.abc.AbstractChannel,
    engine,
):
    async with message.process():
        # получаем сообщение
        request = json.loads(message.body.decode())
        # валидируем
        # если валидно, заносим ответ модели в бд
        if (model_out := validate(request["request"])) == "":
            model_out = predict(request["request"])
            with Session(engine) as session:
                prediction = Prediction(
                    request=request["request"],
                    response=model_out,
                    chat_id=request["chat_id"],
                    cost_id=request["cost_id"],
                    model="gpt2",
                )
                PredictionService(session).create_one(prediction)
                model_out = prediction.prediction_id
            status = "completed"
        else:
            status = "invalid"

        # status может быть invalid
        response = json.dumps(
            {
                # invalid or completed
                "status": status,
                # prediction_id if completed
                # validation description if invalid
                "response": model_out,
            }
        )
        # Отправляем ответ в очередь ответов
        response_message = aio_pika.Message(
            body=response.encode(), correlation_id=message.correlation_id
        )
        await channel.default_exchange.publish(
            response_message, routing_key="responses"
        )


async def main() -> None:
    settings = get_rabbitmq_settings()
    conn = await aio_pika.connect(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        login=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASS,
    )

    channel = await conn.channel()
    requests_queue = await channel.declare_queue(
        "requests",
        durable=True,
        arguments={
            "x-message-ttl": 60000,  # срок существования
            "x-dead-letter-exchange": channel.default_exchange.name,
            "x-dead-letter-routing-key": "responses",
        },  # те же, что и в app
    )
    responses_queue = await channel.declare_queue("responses", durable=True)

    engine = create_engine(get_db_settings().DATABASE_URL_psycopg)

    await requests_queue.consume(
        lambda message: process_message(message, channel, engine)
    )

    try:
        await asyncio.Future()
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
