import asyncio
import aio_pika
import re
import json
import transformers
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from config import get_rabbitmq_settings


tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

model = GPT2LMHeadModel.from_pretrained("gpt2").to("cuda")


def validate(request: str) -> str:
    limit = 50
    pattern = r'^[a-zA-Z0-9,?\'";:!\.\- ]+$'
    if not re.match(pattern, request):
        return "Use only Latin characters, numbers, and punctuation marks.\n"
    if len(request) > limit:
        return f"The text is too long ({len(request)} characters out of {limit})\n"
    return ""


async def process_message(
    message: aio_pika.abc.AbstractIncomingMessage,
    channel: aio_pika.abc.AbstractChannel,
):
    async with message.process():
        request = message.body.decode()
        response = validate(request)
        if response != "":
            return response
        # Токенизация запроса
        input_ids = tokenizer.encode(request, return_tensors="pt").to("cuda")

        attention_mask = input_ids.ne(tokenizer.eos_token_id).long().to("cuda")
        output = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=80,
            num_return_sequences=1,
            temperature=0.7,  # Контроль случайности
            top_k=30,  # Ограничение выбора топ-k токенов
            top_p=0.85,  # Ограничение выбора токенов по cumulative probability
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.5,  # Штраф за повторения
        )

        # Декодируем результат
        response = tokenizer.decode(output[0], skip_special_tokens=True)
        data = json.dumps(
            {
                "model_id": "gpt2",
                "response": response,
            }
        )
        # Отправляем ответ в очередь ответов
        response_message = aio_pika.Message(
            body=data.encode(), correlation_id=message.correlation_id
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
    queue_name = "requests"
    queue = await channel.declare_queue(queue_name, durable=True)
    await queue.consume(lambda message: process_message(message, channel))
    try:
        await asyncio.Future()
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
