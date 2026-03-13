from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.profile import UserProfile
from app.models.recipes import Recipe

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):

    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    recipes = db.query(Recipe).limit(6).all()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "profile": profile,
            "recipes": recipes
        }
    )