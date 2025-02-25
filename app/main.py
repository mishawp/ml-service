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
from utils.fill_db import fill_db, show_db
# from fastapi import FastAPI
# import uvicorn

# app = FastAPI()


# @app.get("/")
# async def index():
#     return {"message": "Hello World"}


if __name__ == "__main__":
    # uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
    init_db()
    print("Init db has been success")
    fill_db()
    print("Fill db has been success")
    show_db()
