from fastapi import APIRouter, Request, status, HTTPException, Depends, Form
from fastapi.responses import Response, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from services.auth.loginform import LoginForm
from database.database import SessionDep
from database.config import get_settings
from models import User
from services.crud import UserService


route = APIRouter(tags=["Home"])
settings = get_settings()


@route.get("/signin")
async def signin(request: Request):
    pass  # html return


@route.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> dict[str, str]:
    user_service = UserService(session)
    user = user_service.read_by_email(form_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    if HashPassword.verify_hash(form_data.password, user.password):
        access_token = create_access_token(user.email)
        response.set_cookie(
            key=settings.COOKIE_NAME,
            value=f"Bearer {access_token}",
            httponly=True,
        )

        return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed.",
    )


@route.post("/login")
async def login(form_data: Annotated[LoginForm, Form()], session: SessionDep):
    response = RedirectResponse("/", status.HTTP_302_FOUND)
    await login_for_access_token(
        response=response, form_data=form_data, session=session
    )
    return response


@route.post("/signup")
async def signup(form_data: Annotated[LoginForm, Form()], session: SessionDep):
    user_service = UserService(session)
    user = user_service.read_by_email(form_data.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user already exists",
        )
    new_user = User(
        email=form_data.username,
        password=HashPassword.create_hash(form_data.password),
    )
    user_service.create_one(new_user)
    response = await login(form_data, session)
    return response


@route.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response
