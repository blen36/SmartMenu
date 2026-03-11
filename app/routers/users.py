from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import SessionLocal
from app.models.user import User
from app.schemas.user_schema import UserCreate

from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)

    new_user = User(
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }