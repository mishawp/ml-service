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
from database.config import get_settings
from database.database import get_session, init_db, engine
from auth.hash_password import HashPassword


def fill_db():
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

        MLModelService.init_model()
        mlmodel_service = MLModelService(session)
        prediction_service = PredictionService(session)

        misha_pred_1 = mlmodel_service.make_prediction(
            request="When she was walking in the park",
            chat_id=misha_chat_1.chat_id,
            cost_id=cost.cost_id,
            timestamp="2024-11-15T14:00:00",
        )

        misha_pred_2 = mlmodel_service.make_prediction(
            request="He decided to take a different route home",
            chat_id=misha_chat_1.chat_id,
            cost_id=cost.cost_id,
            timestamp="2024-11-15T14:30:00",
        )

        misha_pred_3 = mlmodel_service.make_prediction(
            request="The sun was setting behind the mountains",
            chat_id=misha_chat_2.chat_id,
            cost_id=cost.cost_id,
            timestamp="2024-12-05T09:45:00",
        )

        vlad_pred_1 = mlmodel_service.make_prediction(
            request="She found an old book in the attic",
            chat_id=vlad_chat_1.chat_id,
            cost_id=cost.cost_id,
            timestamp="2024-11-22T18:20:00",
        )

        vlad_pred_2 = mlmodel_service.make_prediction(
            request="The cat jumped onto the windowsill",
            chat_id=vlad_chat_1.chat_id,
            cost_id=cost.cost_id,
            timestamp="2025-01-10T12:15:00",
        )

        vlad_pred_3 = mlmodel_service.make_prediction(
            request="They laughed at the joke for hours",
            chat_id=vlad_chat_1.chat_id,
            cost_id=cost.cost_id,
            timestamp="2025-02-01T16:50:00",
        )

        vlad_pred_4 = mlmodel_service.make_prediction(
            request="The rain started just as they left",
            chat_id=vlad_chat_1.chat_id,
            cost_id=cost.cost_id,
            timestamp="2024-12-18T07:00:00",
        )

        lesha_pred_1 = mlmodel_service.make_prediction(
            request="He couldn't believe his eyes",
            chat_id=lesha_chat_1.chat_id,
            cost_id=cost.cost_id,
            timestamp="2025-01-25T20:10:00",
        )

        lesha_pred_2 = mlmodel_service.make_prediction(
            request="The stars were shining brightly",
            chat_id=lesha_chat_1.chat_id,
            cost_id=cost.cost_id,
            timestamp="2024-11-30T22:05:00",
        )

        lesha_pred_3 = mlmodel_service.make_prediction(
            request="She baked cookies for the party",
            chat_id=lesha_chat_1.chat_id,
            cost_id=cost.cost_id,
            timestamp="2025-02-15T10:40:00",
        )

        lesha_pred_4 = mlmodel_service.make_prediction(
            request="The train arrived right on time",
            chat_id=lesha_chat_1.chat_id,
            cost_id=cost.cost_id,
            timestamp="2024-12-25T15:55:00",
        )

        prediction_service.create_one(misha_pred_1)
        prediction_service.create_one(misha_pred_2)
        prediction_service.create_one(misha_pred_3)
        prediction_service.create_one(vlad_pred_1)
        prediction_service.create_one(vlad_pred_2)
        prediction_service.create_one(vlad_pred_3)
        prediction_service.create_one(vlad_pred_4)
        prediction_service.create_one(lesha_pred_1)
        prediction_service.create_one(lesha_pred_2)
        prediction_service.create_one(lesha_pred_3)
        prediction_service.create_one(lesha_pred_4)


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
