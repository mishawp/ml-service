from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class Prediction(SQLModel, table=True):
    prediction_id: int = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default=datetime.now())
    request: str
    cost_id: int = Field(foreign_key="cost.cost_id", ondelete="RESTRICT")
    chat_id: int = Field(foreign_key="chat", ondelete="CASCADE")
    response: str = Field(default=None)
    model: str = Field(default=None)  # не ясно пока
