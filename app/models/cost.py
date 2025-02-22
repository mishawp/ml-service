from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from datetime import datetime


class Cost(SQLModel, table=True):
    cost_id: int = Field(default=None, primary_key=True)
    set_timestamp: datetime = Field(default=datetime.now())
    prediction_cost: Decimal

    # predictions: list["Prediction"] = Relationship(back_populates="cost")
