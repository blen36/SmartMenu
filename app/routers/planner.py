from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from collections import defaultdict

from app.core.dependencies import get_db
from app.models.profile import UserProfile
from app.models.meal_plan import MealPlan
from app.models.interactions import RecipeInteraction
from app.services.menu_service import generate_menu_for_user
from app.services.recipe_search_service import search_recipes
from app.services.nutrition_service import predict_nutrition

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

days_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


@router.get("/planner")
def planner_page(
    request: Request,
    query: str = "",
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    plans = db.query(MealPlan).filter(MealPlan.user_id == user_id).all()

    grouped_plans = defaultdict(list)
    for plan in plans:
        grouped_plans[plan.day_of_week].append(plan)

    recipes = []
    if query:
        recipes = search_recipes(
            query=query,
            translate=True,
            limit=12
        )

    interactions = db.query(RecipeInteraction).filter(
        RecipeInteraction.user_id == user_id
    ).all()

    interaction_map = {}
    for item in interactions:
        if item.recipe_name:
            interaction_map[item.recipe_name] = item.score

    return templates.TemplateResponse(
        "planner.html",
        {
            "request": request,
            "plans": grouped_plans,
            "recipes": recipes,
            "days_order": days_order,
            "query": query,
            "interaction_map": interaction_map
        }
    )


@router.post("/search-recipes")
def search_recipes_route(query: str = Form("")):
    return RedirectResponse(f"/planner?query={query}", status_code=302)


@router.post("/add-meal")
def add_meal(
    request: Request,
    recipe_name: str = Form(...),
    recipe_id: str = Form(""),
    day_of_week: str = Form(...),
    meal_type: str = Form(...),
    calories: int = Form(0),
    protein: int = Form(0),
    fat: int = Form(0),
    carbs: int = Form(0),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    if not calories:
        c, p, f, cb = predict_nutrition(recipe_name)
        calories = int(c)
        protein = int(p)
        fat = int(f)
        carbs = int(cb)

    meal = MealPlan(
        user_id=user_id,
        day_of_week=day_of_week,
        meal_type=meal_type,
        recipe_name=recipe_name,
        recipe_id=str(recipe_id) if recipe_id else None,
        calories=calories,
        protein=protein,
        fat=fat,
        carbs=carbs
    )

    db.add(meal)
    db.commit()

    return RedirectResponse("/planner", status_code=302)


@router.post("/delete-meal/{meal_id}")
def delete_meal(
    meal_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    meal = db.query(MealPlan).filter(
        MealPlan.id == meal_id,
        MealPlan.user_id == user_id
    ).first()

    if meal:
        db.delete(meal)
        db.commit()

    return RedirectResponse("/planner", status_code=302)


@router.post("/clear-plan")
def clear_plan(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    db.query(MealPlan).filter(MealPlan.user_id == user_id).delete()
    db.commit()

    return RedirectResponse("/planner", status_code=302)


@router.get("/generate-ai-menu")
def generate_ai_menu(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not profile:
        return RedirectResponse("/onboarding", status_code=302)

    db.query(MealPlan).filter(MealPlan.user_id == user_id).delete()
    db.commit()

    menu = generate_menu_for_user(profile)

    for item in menu:
        meal = MealPlan(
            user_id=user_id,
            day_of_week=item["day"],
            meal_type=item["meal"],
            recipe_name=item["name"],
            recipe_id=str(item.get("recipe_id")) if item.get("recipe_id") else None,
            calories=int(item.get("calories") or 0),
            protein=int(item.get("protein") or 0),
            fat=int(item.get("fat") or 0),
            carbs=int(item.get("carbs") or 0)
        )
        db.add(meal)

    db.commit()

    return RedirectResponse("/planner", status_code=302)