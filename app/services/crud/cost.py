from sqlmodel import Session, select
from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar
from models.cost import Cost


@dataclass(slots=True)
class CostService:
    current_cost_id: ClassVar[int] = 1
    current_cost: ClassVar[Decimal] = None
    session: Session

    def create_one(self, cost: Cost) -> Cost:
        self.session.add(cost)
        self.session.commit()
        self.session.refresh(cost)
        return cost

    def read_by_id(self, cost_id: int) -> Cost:
        cost = self.session.get(Cost, cost_id)
        return cost if cost else None

    def read_all(self):
        return self.session.exec(select(Cost)).all()

    def read_current_cost(self):
        return self.session.get(Cost, self.current_cost_id)

    def update_by_id(self, cost_id: int, **kwargs) -> Cost:
        cost = self.session.get(Cost, cost_id)
        if not cost:
            raise ValueError(f"Cost with id {cost_id} not found")

        for key, value in kwargs.items():
            if hasattr(cost, key):
                setattr(cost, key, value)
            else:
                raise AttributeError(f"Cost has no attribute {key}")

        self.session.add(cost)
        self.session.commit()
        self.session.refresh(cost)
        return cost

    def delete_by_id(self, cost_id: int) -> Cost:
        cost = self.session.get(Cost, cost_id)
        if not cost:
            raise ValueError(f"Cost with id {cost_id} not found")

        self.session.delete(cost)
        self.session.commit()
        return cost

    def refresh_current_id(self, cost_id: int = None):
        """Обновляет текущую цену, т.е. current_cost_id

        Args:
            cost_id (int, optional): Если None, будет взят Cost.cost_id с самым новым Cost.timestamp. Defaults to None.
        """
        if cost_id is not None:
            cur_cost = self.session.get(Cost, cost_id)
        else:
            cur_cost = select(Cost).order_by(desc(Cost.timestamp)).first()

        if cur_cost:
            self.current_cost_id = cur_cost.cost_id
        else:
            raise ValueError("No Cost records found in the database.")

    def set_current_cost(self) -> Decimal:
        CostService.current_cost = self.read_by_id(
            CostService.current_cost_id
        ).prediction_cost
