from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from app.core.dependencies import get_db
from app.models.interactions import RecipeInteraction

router = APIRouter()


def handle_interaction(
    recipe_id: str,
    request: Request,
    recipe_name: str,
    score: int,
    db: Session
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    existing = db.query(RecipeInteraction).filter(
        RecipeInteraction.user_id == user_id,
        RecipeInteraction.recipe_id == str(recipe_id)
    ).first()

    if existing:
        existing.score = score
        existing.recipe_name = recipe_name
    else:
        db.add(
            RecipeInteraction(
                user_id=user_id,
                recipe_id=str(recipe_id),
                recipe_name=recipe_name,
                score=score
            )
        )

    db.commit()

    referer = request.headers.get("referer", "/dashboard")

    if referer:
        return RedirectResponse(referer, status_code=302)

    return RedirectResponse("/dashboard", status_code=302)


@router.post("/like/{recipe_id}")
def like_recipe(
    recipe_id: str,
    request: Request,
    recipe_name: str = Form(...),
    db: Session = Depends(get_db)
):
    return handle_interaction(recipe_id, request, recipe_name, 1, db)


@router.post("/dislike/{recipe_id}")
def dislike_recipe(
    recipe_id: str,
    request: Request,
    recipe_name: str = Form(...),
    db: Session = Depends(get_db)
):
    return handle_interaction(recipe_id, request, recipe_name, -1, db)