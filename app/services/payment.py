from sqlmodel import Session
from dataclasses import dataclass
from models.payment import Payment


@dataclass(slots=True)
class PaymentService:
    session: Session

    def create_payment(self, payment: Payment) -> Payment:
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def read_payment(self, payment_id: int) -> Payment:
        payment = self.session.get(Payment, payment_id)
        return payment if payment else None

    def update_payment(self, payment_id: int, **kwargs) -> Payment:
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

    def delete_payment(self, payment_id: int) -> Payment:
        payment = self.session.get(Payment, payment_id)
        if not payment:
            raise ValueError(f"Payment with id {payment_id} not found")

        self.session.delete(payment)
        self.session.commit()
        return payment
