from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal


class Person(SQLModel):
    email: str
    password: str = Field(max_length=128)


class User(Person, table=True):
    user_id: int = Field(default=None, primary_key=True)
    balance: Decimal = Field(
        default=Decimal("100.0"), max_digits=10, decimal_places=2
    )


class Admin(Person, table=True):
    admin_id: int = Field(default=None, primary_key=True)
