from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.models.shopping_list import ShoppingList

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/shopping-list")
def shopping_list_page(request: Request, db: Session = Depends(get_db)):

    items = db.query(ShoppingList).all()

    return templates.TemplateResponse(
        "shopping.html",
        {
            "request": request,
            "items": items
        }
    )