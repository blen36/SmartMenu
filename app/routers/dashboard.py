from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.recipes import Recipe

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):

    recipes = db.query(Recipe).limit(3).all()

    # пока значения статические
    calories = 1850
    protein = 120
    fat = 60
    carbs = 210

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "recipes": recipes,
            "calories": calories,
            "protein": protein,
            "fat": fat,
            "carbs": carbs
        }
    )