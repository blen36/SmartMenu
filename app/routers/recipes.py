from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import requests

from app.core.dependencies import get_db
from app.services.nutrition_service import predict_nutrition
from app.models.viewed_recipe import ViewedRecipe
from app.models.nutrition_cache import NutritionCache

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/recipe/{recipe_id}")
def recipe_detail(request: Request, recipe_id: str, db: Session = Depends(get_db)):

    user_id = request.session.get("user_id")

    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={recipe_id}"
    response = requests.get(url)
    data = response.json()

    if not data["meals"]:
        return templates.TemplateResponse(
            "recipe_detail.html",
            {"request": request, "recipe": None}
        )

    meal = data["meals"][0]

    ingredients = []
    ingredient_words = []

    for i in range(1, 21):

        ingredient = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")

        if ingredient and ingredient.strip():
            ingredients.append(f"{ingredient} - {measure}")
            ingredient_words.append(ingredient.lower())

    # текст для ML модели
    recipe_text = meal["strMeal"].lower() + " " + " ".join(ingredient_words)

    # =========================
    # Проверяем кэш КБЖУ
    # =========================

    cache = db.query(NutritionCache).filter(
        NutritionCache.recipe_id == recipe_id
    ).first()

    if cache:

        calories = cache.calories
        protein = cache.protein
        fat = cache.fat
        carbs = cache.carbs

    else:

        try:
            calories, protein, fat, carbs = predict_nutrition(recipe_text)
        except Exception as e:
            print("MODEL ERROR:", e)
            calories, protein, fat, carbs = 0, 0, 0, 0

        cache = NutritionCache(
            recipe_id=recipe_id,
            calories=calories,
            protein=protein,
            fat=fat,
            carbs=carbs
        )

        db.add(cache)
        db.commit()

    # =========================
    # Сохраняем просмотр рецепта
    # =========================

    if user_id:

        existing = db.query(ViewedRecipe).filter(
            ViewedRecipe.user_id == user_id,
            ViewedRecipe.recipe_id == recipe_id
        ).first()

        if not existing:

            viewed = ViewedRecipe(
                user_id=user_id,
                recipe_id=meal["idMeal"],
                recipe_name=meal["strMeal"],
                recipe_image=meal["strMealThumb"],
                calories=calories,
                protein=protein,
                fat=fat,
                carbs=carbs
            )

            db.add(viewed)
            db.commit()

    recipe = {
        "id": meal["idMeal"],
        "name": meal["strMeal"],
        "image": meal["strMealThumb"],
        "instructions": meal["strInstructions"],
        "ingredients": ingredients,
        "category": meal["strCategory"],
        "area": meal["strArea"],
        "youtube": meal["strYoutube"],
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs
    }

    return templates.TemplateResponse(
        "recipe_detail.html",
        {
            "request": request,
            "recipe": recipe
        }
    )