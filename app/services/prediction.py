from sqlmodel import Session, select
from dataclasses import dataclass
from models import Prediction, User, Cost, Chat


@dataclass(slots=True)
class PredictionService:
    session: Session

    def create_prediction(self, prediction: Prediction) -> Prediction:
        chat = self.session.get(Chat, prediction.chat_id)
        user = self.session.get(User, chat.user_id)
        cost = self.session.get(Cost, prediction.cost_id)
        user.balance -= cost.prediction_cost
        self.session.add(prediction)
        self.session.commit()
        self.session.refresh(prediction)
        return prediction

    def read_prediction(self, prediction_id: int) -> Prediction:
        prediction = self.session.get(Prediction, prediction_id)
        return prediction if prediction else None

    def update_prediction(self, prediction_id: int, **kwargs) -> Prediction:
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

    def delete_prediction(self, prediction_id: int) -> Prediction:
        prediction = self.session.get(Prediction, prediction_id)
        if not prediction:
            raise ValueError(f"Prediction with id {prediction_id} not found")

        self.session.delete(prediction)
        self.session.commit()
        return prediction

    def read_all(self):
        return self.session.exec(select(Prediction)).all()
