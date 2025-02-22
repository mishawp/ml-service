from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal

# from sqlalchemy.orm import Mapped, relationship
# from .chat import Chat
# from .payment import Payment


class Person(SQLModel):
    email: str
    password: str = Field(max_length=128)


class User(Person, table=True):
    user_id: int = Field(default=None, primary_key=True)
    balance: Decimal = Field(default=0, max_digits=10, decimal_places=2)

    # chats: list["Chat"] = Relationship(back_populates="user")
    # payments: list["Payment"] = Relationship(back_populates="user")


class Admin(Person, table=True):
    admin_id: int = Field(default=None, primary_key=True)
