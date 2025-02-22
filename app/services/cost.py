from sqlmodel import Session
from dataclasses import dataclass
from models.cost import Cost


@dataclass(slots=True)
class CostService:
    session: Session

    def create_cost(self, cost: Cost) -> Cost:
        self.session.add(cost)
        self.session.commit()
        self.session.refresh(cost)
        return cost

    def read_cost(self, cost_id: int) -> Cost:
        cost = self.session.get(Cost, cost_id)
        return cost if cost else None

    def update_cost(self, cost_id: int, **kwargs) -> Cost:
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

    def delete_cost(self, cost_id: int) -> Cost:
        cost = self.session.get(Cost, cost_id)
        if not cost:
            raise ValueError(f"Cost with id {cost_id} not found")

        self.session.delete(cost)
        self.session.commit()
        return cost
