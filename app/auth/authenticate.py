from fastapi import Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from auth.jwt_handler import verify_access_token
from services.auth.cookieauth import OAuth2PasswordBearerWithCookie
from database.config import get_db_settings

settings = get_db_settings()
oauth2_scheme_cookie = OAuth2PasswordBearerWithCookie(tokenUrl="/token")
templates = Jinja2Templates(directory="view")


async def authenticate_cookie(
    token: str = Depends(oauth2_scheme_cookie),
) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sign in for access"
        )
    token = token.removeprefix("Bearer ")
    decoded_token = verify_access_token(token)
    return decoded_token["user"]
