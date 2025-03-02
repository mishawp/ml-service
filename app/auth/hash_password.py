from dataclasses import dataclass
from typing import ClassVar
from passlib.context import CryptContext


@dataclass(init=False, frozen=True)
class HashPassword:
    pwd_context: ClassVar[CryptContext] = CryptContext(
        schemes=["bcrypt"], deprecated="auto"
    )

    @classmethod
    def create_hash(cls, password: str):
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_hash(cls, plain_password: str, hashed_password: str):
        return cls.pwd_context.verify(plain_password, hashed_password)
