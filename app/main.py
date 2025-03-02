import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.home import route as home_route
from routes.chat import route as chat_route
from routes.user import route as user_route
from database.database import init_db
from database.config import get_settings
from services.crud import MLModelService
from auth.authenticate import authenticate_cookie
from utils.fill_db import fill_db, show_db

settings = get_settings()
app = FastAPI()
app.include_router(home_route)
app.include_router(chat_route)
app.include_router(user_route)

# https://fastapi.tiangolo.com/ru/tutorial/cors/
origins = [
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    MLModelService.init_model()
    fill_db()


@app.get("/", summary="Вход в систему", tags=["Home"])
async def start(request: Request) -> RedirectResponse:
    token = request.cookies.get(settings.COOKIE_NAME)
    user = await authenticate_cookie(token) if token else None
    # context = {"user": user, "request": request}
    if user:
        return RedirectResponse("/chat", status.HTTP_302_FOUND)
    else:
        return RedirectResponse("/signin", status.HTTP_302_FOUND)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
