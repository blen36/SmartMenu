from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.database.db import Base, engine
from app import models

from app.routers import (
    users,
    recipes,
    products,
    planner,
    shopping,
    dashboard,
    onboarding,
    interactions
)

app = FastAPI(title="SmartMenu")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def home(request: Request):
    if request.session.get("user_id"):
        return templates.TemplateResponse(
            "index.html",
            {"request": request}
        )

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


app.include_router(onboarding.router)
app.include_router(users.router)
app.include_router(interactions.router)
app.include_router(recipes.router)
app.include_router(products.router)
app.include_router(planner.router)
app.include_router(shopping.router)
app.include_router(dashboard.router)