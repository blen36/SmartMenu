from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.meal_plan import MealPlan
from app.services.recipe_search_service import search_recipes

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/planner")
def planner_page(request: Request, db: Session = Depends(get_db)):

    user_id = request.session.get("user_id")

    plans = db.query(MealPlan).filter(MealPlan.user_id == user_id).all()

    return templates.TemplateResponse(
        "planner.html",
        {
            "request": request,
            "plans": plans,
            "recipes": []  # чтобы страница не падала
        }
    )


@router.post("/search-recipes")
def search_recipes_route(
        request: Request,
        query: str = Form(""),  # теперь поле не обязательное
        db: Session = Depends(get_db)
):

    user_id = request.session.get("user_id")

    plans = db.query(MealPlan).filter(MealPlan.user_id == user_id).all()

    if query.strip() == "":
        recipes = []
    else:
        recipes = search_recipes(query)

    return templates.TemplateResponse(
        "planner.html",
        {
            "request": request,
            "recipes": recipes,
            "plans": plans
        }
    )


@router.post("/add-meal")
def add_meal(
        request: Request,
        recipe_name: str = Form(...),
        day_of_week: str = Form(...),
        db: Session = Depends(get_db)
):

    user_id = request.session.get("user_id")

    plan = MealPlan(
        user_id=user_id,
        day_of_week=day_of_week,
        recipe_name=recipe_name
    )

    db.add(plan)
    db.commit()

    return RedirectResponse("/planner", status_code=302)