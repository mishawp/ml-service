from sqlmodel import Session
from models import Chat, Cost, Payment, User, Admin, Prediction
from services import (
    ChatService,
    CostService,
    PaymentService,
    UserService,
    AdminService,
    PredictionService,
)
from database.config import get_settings
from database.database import get_session, init_db, engine
# from fastapi import FastAPI
# import uvicorn

# app = FastAPI()


# @app.get("/")
# async def index():
#     return {"message": "Hello World"}


if __name__ == "__main__":
    # uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

    test_user = User(email="test@mail.ru", password="test")
    test_user_2 = User(email="test@mail.ru", password="test")
    test_user_3 = User(email="test@mail.ru", password="test")

    init_db()
    print("Init db has been success")

    with Session(engine) as session:
        user_service = UserService(session)
        user_service.create_user(test_user)
        user_service.create_user(test_user_2)
        user_service.create_user(test_user_3)
        users = user_service.read_all()

    print(users, type(users))
    for user in users:
        print(f"id: {user.user_id} - {user.email}")
