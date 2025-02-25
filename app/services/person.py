from sqlmodel import Session, select
from dataclasses import dataclass
from models import User, Admin, Payment


@dataclass(slots=True)
class UserService:
    session: Session

    def create_user(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def read_user(self, user_id: int) -> User:
        user = self.session.get(User, user_id)
        return user if user else None

    def update_user(self, user_id: int, **kwargs) -> User:
        user = self.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                raise AttributeError(f"User has no attribute {key}")

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete_user(self, user_id: int) -> User:
        user = self.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        self.session.delete(user)
        self.session.commit()
        return user

    def read_all(self):
        return self.session.exec(select(User)).all()


@dataclass(slots=True)
class AdminService:
    session: Session

    def create_admin(self, admin: Admin) -> Admin:
        self.session.add(admin)
        self.session.commit()
        self.session.refresh(admin)
        return admin

    def read_admin(self, admin_id: int) -> Admin:
        admin = self.session.get(Admin, admin_id)
        return admin if admin else None

    def update_admin(self, admin_id: int, **kwargs) -> Admin:
        admin = self.session.get(Admin, admin_id)
        if not admin:
            raise ValueError(f"Admin with id {admin_id} not found")

        for key, value in kwargs.items():
            if hasattr(admin, key):
                setattr(admin, key, value)
            else:
                raise AttributeError(f"Admin has no attribute {key}")

        self.session.add(admin)
        self.session.commit()
        self.session.refresh(admin)
        return admin

    def delete_admin(self, admin_id: int) -> Admin:
        admin = self.session.get(Admin, admin_id)
        if not admin:
            raise ValueError(f"Admin with id {admin_id} not found")

        self.session.delete(admin)
        self.session.commit()
        return admin

    def read_all(self):
        return self.session.exec(select(Admin)).all()

    def confirm_payment(self, payment_id: int):
        payment = self.session.get(Payment, payment_id)

        if not payment:
            raise ValueError(f"Payment with id {payment_id} not found")

        user = self.session.get(User, payment.user_id)

        if payment.status == False:
            user.balance += payment.amount
            payment.status = True
        else:
            print("The payment has already been confirmed")
        self.session.commit()
