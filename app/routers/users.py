from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.models.profile import UserProfile
from app.ai.nutrition_calculator import calculate_targets

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def create_or_update_profile(db: Session, user_id: int, data: dict):
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


@router.get("/register-page")
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "has_onboarding": bool(request.session.get("onboarding_data"))
        }
    )


@router.get("/login-page")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/register-form")
def register_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Пользователь с таким email уже существует",
                "has_onboarding": bool(request.session.get("onboarding_data"))
            }
        )

    user = User(
        email=email,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id

    onboarding_data = request.session.get("onboarding_data")

    if onboarding_data:
        create_or_update_profile(db, user.id, onboarding_data)
        request.session.pop("onboarding_data", None)
        return RedirectResponse("/dashboard", status_code=302)

    return RedirectResponse("/onboarding", status_code=302)


@router.post("/login-form")
def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Неверный email или пароль"
            }
        )

    request.session["user_id"] = user.id

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    if not profile:
        return RedirectResponse("/onboarding", status_code=302)

    return RedirectResponse("/dashboard", status_code=302)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)


@router.get("/profile")
def profile_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "profile": profile
        }
    )


@router.get("/profile-form")
def profile_form(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    return templates.TemplateResponse(
        "profile_form.html",
        {
            "request": request,
            "profile": profile
        }
    )


@router.post("/save-profile")
def save_profile(
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
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    data = {
        "age": age,
        "height": height,
        "weight": weight,
        "gender": gender,
        "activity_level": activity_level,
        "goal": goal,
        "allergies": allergies
    }

    create_or_update_profile(db, user_id, data)

    return RedirectResponse("/dashboard", status_code=302)