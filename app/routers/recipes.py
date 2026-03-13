from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.models.recipes import Recipe

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/recipes")
def recipes_page(request: Request, db: Session = Depends(get_db)):

    recipes = db.query(Recipe).all()

    return templates.TemplateResponse(
        "recipes.html",
        {
            "request": request,
            "recipes": recipes
        }
    )