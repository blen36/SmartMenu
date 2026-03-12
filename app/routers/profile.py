from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.profile import UserProfile

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/profile")
def profile_page(request: Request, db: Session = Depends(get_db)):

    profile = db.query(UserProfile).filter(UserProfile.user_id == 1).first()

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "profile": profile
        }
    )