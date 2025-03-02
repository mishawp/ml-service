from sqlmodel import Session, select
from dataclasses import dataclass
from models import Prediction, User, Cost, Chat


@dataclass(slots=True)
class PredictionService:
    session: Session

    def create_one(self, prediction: Prediction) -> Prediction:
        chat = self.session.get(Chat, prediction.chat_id)
        user = self.session.get(User, chat.user_id)
        cost = self.session.get(Cost, prediction.cost_id)
        user.balance -= cost.prediction_cost
        if chat.name is None:
            chat.name = prediction.response[
                : min(12, len(prediction.response))
            ]
        self.session.add(prediction)
        self.session.commit()
        self.session.refresh(prediction)
        return prediction

    def read_by_id(self, prediction_id: int) -> Prediction:
        prediction = self.session.get(Prediction, prediction_id)
        return prediction if prediction else None

    def read_by_chat_id(self, chat_id: int):
        return self.session.exec(
            select(Prediction).where(Prediction.chat_id == chat_id)
        ).all()

    def read_all(self) -> list[Prediction]:
        return self.session.exec(select(Prediction)).all()

    def update_by_id(self, prediction_id: int, **kwargs) -> Prediction:
        prediction = self.session.get(Prediction, prediction_id)
        if not prediction:
            raise ValueError(f"Prediction with id {prediction_id} not found")

        for key, value in kwargs.items():
            if hasattr(prediction, key):
                setattr(prediction, key, value)
            else:
                raise AttributeError(f"Prediction has no attribute {key}")

        self.session.add(prediction)
        self.session.commit()
        self.session.refresh(prediction)
        return prediction

    def delete_by_id(self, prediction_id: int) -> Prediction:
        prediction = self.session.get(Prediction, prediction_id)
        if not prediction:
            raise ValueError(f"Prediction with id {prediction_id} not found")

        self.session.delete(prediction)
        self.session.commit()
        return prediction
