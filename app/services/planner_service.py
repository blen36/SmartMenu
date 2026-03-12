from sqlalchemy.orm import Session
from app.models.meal_plan import MealPlan
from app.models.recipes import Recipe


def get_user_plan(db: Session, user_id: int):

    plans = db.query(MealPlan).filter(MealPlan.user_id == user_id).all()

    return plans


def create_meal_plan(db: Session, user_id: int, day_of_week: str, recipe_id: int):

    plan = MealPlan(
        user_id=user_id,
        day_of_week=day_of_week,
        recipe_id=recipe_id
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan


def get_all_recipes(db: Session):

    return db.query(Recipe).all()