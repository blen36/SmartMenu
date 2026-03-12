from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from passlib.context import CryptContext

from app.database.db import SessionLocal
from app.models.user import User
from app.models.profile import UserProfile

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"error": "user not found"}

    if not pwd_context.verify(password, user.password):
        return {"error": "wrong password"}

    return RedirectResponse("/dashboard", status_code=302)


@router.get("/profile-form")
def profile_form(request: Request):
    return templates.TemplateResponse("profile_form.html", {"request": request})


@router.post("/save-profile")
def save_profile(
        age: int = Form(...),
        height: int = Form(...),
        weight: int = Form(...),
        goal: str = Form(...),
        allergies: str = Form(...),
        db: Session = Depends(get_db)
):

    profile = UserProfile(
        user_id=1,
        age=age,
        height=height,
        weight=weight,
        goal=goal,
        allergies=allergies
    )

    db.add(profile)
    db.commit()

    return RedirectResponse("/profile", status_code=302)


@router.get("/profile")
def view_profile(request: Request, db: Session = Depends(get_db)):

    profile = db.query(UserProfile).first()

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "profile": profile
        }
    )