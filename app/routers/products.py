from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.database.db import SessionLocal
from app.models.product import Product

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/products")
def products_page(request: Request, db: Session = Depends(get_db)):

    products = db.query(Product).all()

    return templates.TemplateResponse(
        "products.html",
        {
            "request": request,
            "products": products
        }
    )