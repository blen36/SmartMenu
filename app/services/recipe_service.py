from sqlalchemy.orm import Session
from app.models.recipes import Recipe


def get_all_recipes(db: Session):

    return db.query(Recipe).all()


def create_recipe(db: Session, recipe_data):

    recipe = Recipe(**recipe_data)

    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return recipe