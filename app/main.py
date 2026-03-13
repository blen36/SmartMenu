from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.middleware.sessions import SessionMiddleware

from app.database.db import Base, engine
from app import models

from app.routers import users, recipes, products, planner, shopping, dashboard, onboarding

app = FastAPI()

# сессии пользователей
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key"
)

# создаем таблицы
Base.metadata.create_all(bind=engine)

# templates
templates = Jinja2Templates(directory="app/templates")

# static
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# routers
app.include_router(users.router)
app.include_router(recipes.router)
app.include_router(products.router)
app.include_router(planner.router)
app.include_router(shopping.router)
app.include_router(dashboard.router)
app.include_router(onboarding.router)