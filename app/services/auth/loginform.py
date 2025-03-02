from fastapi import Request
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated


class LoginForm(BaseModel):
    username: EmailStr
    password: Annotated[str, Field(min_length=1)]
    model_config = {"extra": "forbid"}
