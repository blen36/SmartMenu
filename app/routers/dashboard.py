from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.profile import UserProfile
from app.models.interactions import RecipeInteraction
from app.services.recommendation_service import get_recommendations

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    recipes = get_recommendations(db, user_id)

    interactions = db.query(RecipeInteraction).filter(
        RecipeInteraction.user_id == user_id
    ).all()

    interaction_map = {}
    for item in interactions:
        if item.recipe_name:
            interaction_map[item.recipe_name] = item.score

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "profile": profile,
            "recipes": recipes,
            "interaction_map": interaction_map
        }
    )