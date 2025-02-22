# from dataclasses import dataclass, field
# from abc import ABC
# from decimal import Decimal
# from datetime import datetime
# from typing import Any


# @dataclass(slots=True)
# class Payment:
#     __id: int
#     __timestamp: datetime
#     __amount: Decimal
#     __user_id: int
#     __status: bool

#     def change_status(self):
#         pass

#     # по необходимости будут еще


# @dataclass(init=False)
# class Balance:
#     @staticmethod
#     def increase_balance(user_id: int):
#         pass

#     @staticmethod
#     def decrease_balance(user_id: int):
#         pass


# @dataclass(slots=True)
# class Prediction:
#     __id: int
#     __timestamp: datetime
#     __request: str
#     __cost_id: int
#     __chat_id: int
#     __response: str = field(default=None, init=False)
#     __model_id: int = field(default=None, init=False)

#     def predict(self):
#         # здесь установятся __response и __model_id
#         # Как сюда попадет MLModel пока не знаю
#         pass

#     def __validate(self):
#         pass


# @dataclass(slots=True)
# class Chat:
#     __id: int
#     __user_id: int
#     __name: str

#     def open(self) -> list[Prediction]:
#         pass

#     # может и не нужен
#     def close(self):
#         pass


# @dataclass(init=False)
# class CRUDChat:
#     @staticmethod
#     def create_chat(user_id: int) -> Chat:
#         pass

#     @staticmethod
#     def read_chat(chat_id: int) -> Chat:
#         pass

#     @staticmethod
#     def update_chat(chat_id: int) -> Chat:
#         # как минимум имя чата поменять
#         pass

#     @staticmethod
#     def delete_chat(chat_id: int):
#         pass


# @dataclass(slots=True)
# class Person(ABC):
#     __id: int  # автоинкремент, но нужно учесть связь с бд
#     __email: str
#     __password: str  # или другой специализированный тип


# @dataclass(slots=True)
# class User(Person):
#     __balance: float

#     def pay(self, amount: Decimal):
#         pass

#     def show_payments(self) -> list[Payment]:
#         pass

#     def show_chats(self) -> list[Chat]:
#         pass

#     def predict(self, request: str) -> Prediction:
#         pass

#     def __check_balance(self) -> bool:
#         pass


# @dataclass(slots=True)
# class Admin(Person):
#     def show_payments(self, user_id: int) -> list[Payment]:
#         pass

#     def moderate_payment(self, payment_id: int):
#         # управление Payment-ом происходит через его интерфейс,
#         # т.к. он связан с User
#         pass


# @dataclass(init=False)
# class Authorization:
#     @staticmethod
#     def sign_up(email: str, password: str, admin: bool) -> str | Person:
#         # возвращает статус или создает пользователя
#         pass

#     @staticmethod
#     def log_in(email: str, password: str) -> str | Person:
#         # возвращает статус или авторизует пользователя
#         pass


# @dataclass(slots=True)
# class Cost:
#     __id: int
#     __set_timestamp: datetime
#     __prediction_cost: float
#     __change_timestamp: datetime

#     def change_cost(value: float):
#         # только вот кто будет управлять ценой? Но пускай будет
#         pass


# @dataclass(slots=True)
# class MLModel:
#     # или другой тип, смотря, что будет в бд
#     __id: int = field(default=None, init=False)
#     __model: Any = field(default=None, init=False)

#     def init_model(self) -> Any:
#         """Загружает модель в систему. Пока не ясно"""
#         pass

#     def predict(request: str) -> str:
#         # __model.predict()
#         pass
