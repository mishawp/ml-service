import asyncio
from sqlmodel import Session
from decimal import Decimal
from datetime import datetime
from models import Chat, Cost, Payment, User, Admin, Prediction
from services.crud import (
    ChatService,
    CostService,
    PaymentService,
    UserService,
    AdminService,
    PredictionService,
    MLModelService,
)
from database.database import init_db, engine
from rabbitmq.rabbitmq import get_connection
from auth.hash_password import HashPassword


# подстраиваемся под код рабочего приложения
async def predict(
    mlmodel_service: MLModelService,
    prediction_service: PredictionService,
    chat: Chat,
    model_input: str,
) -> None:
    await mlmodel_service.publish_ml_task(
        model_input=model_input,
        chat_id=chat.chat_id,
    )
    while True:
        mlmodel_out = await mlmodel_service.receive_any_ml_task()
        if mlmodel_out["status"] == "no_tasks":
            continue
        else:
            prediction_service.create_one(
                Prediction(
                    request=mlmodel_out["model_input"],
                    response=mlmodel_out["response"],
                    chat_id=mlmodel_out["chat_id"],
                    cost_id=CostService.current_cost_id,
                    model=mlmodel_out["model"],
                )
            )
            break


async def fill_db():
    # users/admin

    with Session(engine) as session:
        user_service = UserService(session)
        misha = User(
            email="misha@mail.ru", password=HashPassword.create_hash("misha")
        )
        vlad = User(
            email="vlad@mail.ru", password=HashPassword.create_hash("vlad")
        )
        lesha = User(
            email="lesha@mail.ru", password=HashPassword.create_hash("lesha")
        )
        admin = Admin(
            email="admin@mail.ru", password=HashPassword.create_hash("admin")
        )
        user_service.create_one(misha)
        user_service.create_one(vlad)
        user_service.create_one(lesha)

        admin_service = AdminService(session)
        admin_service.create_one(admin)

        # chats
        misha_chat_1 = Chat(user_id=misha.user_id)
        misha_chat_2 = Chat(user_id=misha.user_id)
        vlad_chat_1 = Chat(user_id=vlad.user_id)
        lesha_chat_1 = Chat(user_id=lesha.user_id)

        chat_service = ChatService(session)
        chat_service.create_one(misha_chat_1)
        chat_service.create_one(misha_chat_2)
        chat_service.create_one(vlad_chat_1)
        chat_service.create_one(lesha_chat_1)

        # payments
        misha_payment_1 = Payment(
            amount=Decimal("50.0"),
            user_id=misha.user_id,
            timestamp=datetime(
                year=2024, month=12, day=12, hour=12, minute=12, second=12
            ),
        )
        misha_payment_2 = Payment(
            amount=Decimal("100.0"),
            user_id=misha.user_id,
            timestamp=datetime(
                year=2025, month=1, day=12, hour=12, minute=12, second=12
            ),
        )
        vlad_payment_1 = Payment(
            amount=Decimal("500.0"),
            user_id=vlad.user_id,
            timestamp=datetime(
                year=2025, month=1, day=25, hour=13, minute=20, second=30
            ),
        )
        vlad_payment_2 = Payment(
            amount=Decimal("700.0"),
            user_id=vlad.user_id,
            timestamp=datetime(
                year=2024, month=10, day=4, hour=10, minute=1, second=1
            ),
        )
        lesha_payment_1 = Payment(
            amount=Decimal("5.0"),
            user_id=lesha.user_id,
            timestamp=datetime(
                year=2025, month=2, day=20, hour=19, minute=24, second=11
            ),
        )
        lesha_payment_2 = Payment(
            amount=Decimal("10.0"),
            user_id=lesha.user_id,
            timestamp=datetime(
                year=2025, month=2, day=23, hour=16, minute=4, second=32
            ),
        )

        payment_service = PaymentService(session)
        payment_service.create_one(misha_payment_1)
        admin_service.confirm_payment(misha_payment_1.payment_id)
        payment_service.create_one(misha_payment_2)
        admin_service.confirm_payment(misha_payment_2.payment_id)
        payment_service.create_one(vlad_payment_1)
        admin_service.confirm_payment(vlad_payment_1.payment_id)
        payment_service.create_one(vlad_payment_2)
        admin_service.confirm_payment(vlad_payment_2.payment_id)
        payment_service.create_one(lesha_payment_1)
        admin_service.confirm_payment(lesha_payment_1.payment_id)
        payment_service.create_one(lesha_payment_2)
        admin_service.confirm_payment(lesha_payment_2.payment_id)

        # Costs

        cost = Cost(prediction_cost=Decimal("2.0"))

        cost_service = CostService(session)
        cost_service.create_one(cost)
        cost_service.set_current_cost()
        async with get_connection().channel() as channel:
            mlmodel_service = MLModelService(channel, "...", session)
            print(MLModelService.shared_requests_queue)
            prediction_service = PredictionService(session)

            # 1
            mlmodel_service.username = misha.email
            await predict(
                mlmodel_service,
                prediction_service,
                misha_chat_1,
                "When she was walking in the park",
            )

            # 2
            await predict(
                mlmodel_service,
                prediction_service,
                misha_chat_1,
                "He decided to take a different route home",
            )

            # 3
            await predict(
                mlmodel_service,
                prediction_service,
                misha_chat_2,
                "The sun was setting behind the mountains",
            )

            mlmodel_service.username = vlad.email
            # 4
            await predict(
                mlmodel_service,
                prediction_service,
                vlad_chat_1,
                "She found an old book in the attic",
            )

            # 5
            await predict(
                mlmodel_service,
                prediction_service,
                vlad_chat_1,
                "The cat jumped onto the windowsill",
            )

            # 6
            await predict(
                mlmodel_service,
                prediction_service,
                vlad_chat_1,
                "They laughed at the joke for hours",
            )

            # 7
            await predict(
                mlmodel_service,
                prediction_service,
                vlad_chat_1,
                "The rain started just as they left",
            )

            mlmodel_service.username = lesha.email
            # 8
            await predict(
                mlmodel_service,
                prediction_service,
                lesha_chat_1,
                "He couldn't believe his eyes",
            )

            # 9
            await predict(
                mlmodel_service,
                prediction_service,
                lesha_chat_1,
                "The stars were shining brightly",
            )

            # 10
            await predict(
                mlmodel_service,
                prediction_service,
                lesha_chat_1,
                "She baked cookies for the party",
            )

            # 11
            await predict(
                mlmodel_service,
                prediction_service,
                lesha_chat_1,
                "The train arrived right on time",
            )


def show_db():
    services = [
        ChatService,
        CostService,
        PaymentService,
        UserService,
        AdminService,
        PredictionService,
    ]

    # вот и полиморфизм
    with Session(engine) as session:
        for service in services:
            print("-------------------------------------------")
            print(service.__name__)
            service = service(session)
            records = service.read_all()
            for record in records:
                print(record.__dict__)
                print("***")
            print("-------------------------------------------")


if __name__ == "__main__":
    init_db()
    print("Init db has been success")
    fill_db()
