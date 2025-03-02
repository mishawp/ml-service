from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from datetime import datetime


class Payment(SQLModel, table=True):
    payment_id: int = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default=datetime.now())
    amount: Decimal
    user_id: int = Field(foreign_key="user.user_id", ondelete="RESTRICT")
    status: bool = Field(default=False)
