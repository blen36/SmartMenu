from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.profile import UserProfile
from app.ai.nutrition_calculator import calculate_targets

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def save_profile_from_data(db: Session, user_id: int, data: dict):
    targets = calculate_targets(
        weight=float(data["weight"]),
        height=float(data["height"]),
        age=int(data["age"]),
        gender=data["gender"],
        activity_level=data["activity_level"],
        goal=data["goal"]
    )

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    profile.age = int(data["age"])
    profile.height = float(data["height"])
    profile.weight = float(data["weight"])
    profile.gender = data["gender"]
    profile.activity_level = data["activity_level"]
    profile.goal = data["goal"]
    profile.allergies = data.get("allergies", "")

    profile.daily_calories = targets["calories"]
    profile.daily_protein = targets["protein"]
    profile.daily_fat = targets["fat"]
    profile.daily_carbs = targets["carbs"]

    db.commit()
    db.refresh(profile)

    return profile


@router.get("/onboarding")
def onboarding_page(request: Request):
    saved_data = request.session.get("onboarding_data", {})

    return templates.TemplateResponse(
        "onboarding.html",
        {
            "request": request,
            "data": saved_data
        }
    )


@router.get("/onboarding/{step}")
def old_onboarding_redirect(step: int):
    return RedirectResponse("/onboarding", status_code=302)


@router.post("/onboarding")
def save_onboarding(
    request: Request,
    age: int = Form(...),
    height: float = Form(...),
    weight: float = Form(...),
    gender: str = Form(...),
    activity_level: str = Form(...),
    goal: str = Form(...),
    allergies: str = Form(""),
    db: Session = Depends(get_db)
):
    data = {
        "age": age,
        "height": height,
        "weight": weight,
        "gender": gender,
        "activity_level": activity_level,
        "goal": goal,
        "allergies": allergies
    }

    user_id = request.session.get("user_id")

    if user_id:
        save_profile_from_data(db, user_id, data)
        return RedirectResponse("/dashboard", status_code=302)

    request.session["onboarding_data"] = data

    return RedirectResponse("/register-page", status_code=302)