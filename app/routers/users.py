from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.dependencies import get_db
from app.models.user import User
from app.models.profile import UserProfile

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/register-page")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login-page")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/register-form")
def register_form(
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):

    hashed_password = pwd_context.hash(password)

    new_user = User(email=email, password=hashed_password)

    db.add(new_user)
    db.commit()

    return RedirectResponse("/login-page", status_code=302)


@router.post("/login-form")
def login_form(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == email).first()

    if not user:

        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Пользователь не найден"
            }
        )

    if not pwd_context.verify(password, user.password):

        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Неверный пароль"
            }
        )

    request.session["user_id"] = user.id

    return RedirectResponse("/dashboard", status_code=302)

@router.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse("/login-page", status_code=302)


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
        height: int = Form(...),
        weight: int = Form(...),
        goal: str = Form(...),
        allergies: str = Form(...),
        db: Session = Depends(get_db)
):

    user_id = request.session.get("user_id")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if profile:

        profile.age = age
        profile.height = height
        profile.weight = weight
        profile.goal = goal
        profile.allergies = allergies

    else:

        profile = UserProfile(
            user_id=user_id,
            age=age,
            height=height,
            weight=weight,
            goal=goal,
            allergies=allergies
        )

        db.add(profile)

    db.commit()

    return RedirectResponse("/profile", status_code=302)