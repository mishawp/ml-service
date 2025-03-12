import uvicorn
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.home import route as home_route
from routes.chat import route as chat_route
from routes.user import route as user_route
from database.config import get_db_settings
from database.database import init_db
from rabbitmq.rabbitmq import (
    connect_rabbitmq,
    close_rabbitmq_connection,
)
from auth.authenticate import authenticate_cookie
from utils.fill_db import fill_db, show_db

templates = Jinja2Templates(directory="view")
settings = get_db_settings()
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


# Middleware для обработки исключений
@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as e:
        if e.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]:
            error_message = e.detail
            return RedirectResponse(
                url=f"/signin?error={error_message}",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        raise


@app.on_event("startup")
async def on_startup():
    init_db()
    await connect_rabbitmq()
    await fill_db()


@app.on_event("shutdown")
async def shutdown_event():
    await close_rabbitmq_connection()


@app.get("/", summary="Вход в систему", tags=["Home"])
async def start(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
