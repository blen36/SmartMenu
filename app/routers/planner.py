from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.services.planner_service import get_user_plan, create_meal_plan, get_all_recipes

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/planner")
def planner_page(request: Request, db: Session = Depends(get_db)):

    recipes = get_all_recipes(db)

    plans = get_user_plan(db, user_id=1)

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
    day_of_week: str = Form(...),
    recipe_id: int = Form(...),
    db: Session = Depends(get_db)
):

    create_meal_plan(
        db=db,
        user_id=1,
        day_of_week=day_of_week,
        recipe_id=recipe_id
    )

    return RedirectResponse("/planner", status_code=302)