from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import requests

from app.core.dependencies import get_db
from app.core.config import settings
from app.models.shopping_list import ShoppingList
from app.models.meal_plan import MealPlan

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


SPOONACULAR_INGREDIENT_IMAGE_BASE = "https://spoonacular.com/cdn/ingredients_250x250/"


def get_user_id_or_redirect(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        return None

    return user_id


def search_spoonacular_ingredients(query: str, limit: int = 12):
    if not query or not query.strip():
        return []

    try:
        response = requests.get(
            "https://api.spoonacular.com/food/ingredients/autocomplete",
            params={
                "query": query.strip(),
                "number": limit,
                "metaInformation": "true",
                "apiKey": settings.SPOONACULAR_API_KEY
            },
            timeout=8
        )

        response.raise_for_status()
        data = response.json()

        products = []

        for item in data:
            name = item.get("name")
            image = item.get("image")

            if not name:
                continue

            image_url = None

            if image:
                image_url = SPOONACULAR_INGREDIENT_IMAGE_BASE + image

            products.append({
                "name": name,
                "image": image_url,
                "aisle": item.get("aisle") or "Ingredient"
            })

        return products

    except Exception as e:
        print("Spoonacular ingredient search error:", e)
        return []


def get_themealdb_ingredients(recipe_id: str):
    if not recipe_id:
        return []

    try:
        response = requests.get(
            "https://www.themealdb.com/api/json/v1/1/lookup.php",
            params={"i": recipe_id},
            timeout=8
        )

        response.raise_for_status()
        data = response.json()

        meals = data.get("meals") or []

        if not meals:
            return []

        meal = meals[0]
        ingredients = []

        for index in range(1, 21):
            ingredient = meal.get(f"strIngredient{index}")
            measure = meal.get(f"strMeasure{index}")

            if ingredient and ingredient.strip():
                ingredients.append({
                    "name": ingredient.strip(),
                    "quantity": measure.strip() if measure and measure.strip() else "1"
                })

        return ingredients

    except Exception as e:
        print("TheMealDB ingredients error:", e)
        return []


def find_ingredient_image(name: str):
    results = search_spoonacular_ingredients(name, limit=1)

    if results:
        return results[0].get("image")

    return None


@router.get("/shopping-list")
def shopping_page(request: Request, db: Session = Depends(get_db)):
    user_id = get_user_id_or_redirect(request)

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    items = db.query(ShoppingList).filter(
        ShoppingList.user_id == user_id
    ).order_by(ShoppingList.id.desc()).all()

    return templates.TemplateResponse(
        "shopping.html",
        {
            "request": request,
            "items": items,
            "products": [],
            "query": "",
            "error": None
        }
    )


@router.post("/search-products")
def search_products(
    request: Request,
    query: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = get_user_id_or_redirect(request)

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    items = db.query(ShoppingList).filter(
        ShoppingList.user_id == user_id
    ).order_by(ShoppingList.id.desc()).all()

    products = search_spoonacular_ingredients(query)

    error = None

    if not products:
        error = (
            "Не удалось найти ингредиенты через Spoonacular. "
            "Попробуйте более простой запрос на английском, например: chicken, milk, rice."
        )

    return templates.TemplateResponse(
        "shopping.html",
        {
            "request": request,
            "items": items,
            "products": products,
            "query": query,
            "error": error
        }
    )


@router.post("/add-product")
def add_product(
    request: Request,
    product_name: str = Form(...),
    quantity: str = Form("1"),
    image: str = Form(""),
    db: Session = Depends(get_db)
):
    user_id = get_user_id_or_redirect(request)

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    existing = db.query(ShoppingList).filter(
        ShoppingList.user_id == user_id,
        ShoppingList.product_name.ilike(product_name)
    ).first()

    if existing:
        if existing.quantity:
            existing.quantity = f"{existing.quantity}, {quantity}"
        else:
            existing.quantity = quantity

        if not existing.image and image:
            existing.image = image
    else:
        item = ShoppingList(
            user_id=user_id,
            product_name=product_name,
            quantity=quantity,
            image=image if image else None
        )

        db.add(item)

    db.commit()

    return RedirectResponse("/shopping-list", status_code=302)


@router.post("/delete-item/{item_id}")
def delete_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = get_user_id_or_redirect(request)

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    item = db.query(ShoppingList).filter(
        ShoppingList.id == item_id,
        ShoppingList.user_id == user_id
    ).first()

    if item:
        db.delete(item)
        db.commit()

    return RedirectResponse("/shopping-list", status_code=302)


@router.post("/clear-cart")
def clear_cart(request: Request, db: Session = Depends(get_db)):
    user_id = get_user_id_or_redirect(request)

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    db.query(ShoppingList).filter(
        ShoppingList.user_id == user_id
    ).delete()

    db.commit()

    return RedirectResponse("/shopping-list", status_code=302)


@router.get("/generate-shopping-week")
def generate_shopping_week(request: Request, db: Session = Depends(get_db)):
    user_id = get_user_id_or_redirect(request)

    if not user_id:
        return RedirectResponse("/login-page", status_code=302)

    plans = db.query(MealPlan).filter(
        MealPlan.user_id == user_id
    ).all()

    added_count = 0

    for plan in plans:
        if not plan.recipe_id:
            continue

        ingredients = get_themealdb_ingredients(str(plan.recipe_id))

        for ingredient in ingredients:
            name = ingredient["name"]
            quantity = ingredient["quantity"]

            existing = db.query(ShoppingList).filter(
                ShoppingList.user_id == user_id,
                ShoppingList.product_name.ilike(name)
            ).first()

            if existing:
                if quantity and quantity not in existing.quantity:
                    existing.quantity = f"{existing.quantity}, {quantity}"
            else:
                image = find_ingredient_image(name)

                item = ShoppingList(
                    user_id=user_id,
                    product_name=name,
                    quantity=quantity,
                    image=image
                )

                db.add(item)
                added_count += 1

    db.commit()

    return RedirectResponse("/shopping-list", status_code=302)