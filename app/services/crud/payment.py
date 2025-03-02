from sqlmodel import Session, select
from dataclasses import dataclass
from models import Payment, User


@dataclass(slots=True)
class PaymentService:
    session: Session

    def create_one(self, payment: Payment) -> Payment:
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def read_by_id(self, payment_id: int) -> Payment:
        payment = self.session.get(Payment, payment_id)
        return payment

    def read_by_user_id(self, user_id: int) -> list[Payment]:
        return self.session.exec(
            select(Payment).where(Payment.user_id == user_id)
        ).all()

    def read_all(self):
        return self.session.exec(select(Payment)).all()

    def update_by_id(self, payment_id: int, **kwargs) -> Payment:
        payment = self.session.get(Payment, payment_id)
        if not payment:
            raise ValueError(f"Payment with id {payment_id} not found")

        for key, value in kwargs.items():
            if hasattr(payment, key):
                setattr(payment, key, value)
            else:
                raise AttributeError(f"Payment has no attribute {key}")

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def delete_by_id(self, payment_id: int) -> Payment:
        payment = self.session.get(Payment, payment_id)
        if not payment:
            raise ValueError(f"Payment with id {payment_id} not found")

        self.session.delete(payment)
        self.session.commit()
        return payment

    def update_user_balance(self, user: User, payment: Payment) -> None:
        if payment.status == False:
            user.balance += payment.amount
            payment.status = True
            self.session.commit()
