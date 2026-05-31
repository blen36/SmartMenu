import time
import re
import requests
from deep_translator import GoogleTranslator

from app.services.nutrition_service import predict_nutrition


THEMEALDB_DISABLED_UNTIL = 0
THEMEALDB_CACHE = {}


def is_themealdb_disabled():
    return time.time() < THEMEALDB_DISABLED_UNTIL


def disable_themealdb(seconds=20):
    global THEMEALDB_DISABLED_UNTIL
    THEMEALDB_DISABLED_UNTIL = time.time() + seconds


def translate_query(query: str) -> str:
    try:
        return GoogleTranslator(source="auto", target="en").translate(query)
    except Exception:
        return query


def clean_query(query: str) -> str:
    query = str(query)

    query = re.sub(r"\([^)]*\)", " ", query)
    query = query.replace("Recipe", " ")
    query = query.replace("recipe", " ")
    query = query.replace("Low Calorie", " ")
    query = query.replace("Low-Calorie", " ")
    query = query.replace("High Protein", " ")
    query = query.replace("Low Fat", " ")

    query = re.sub(r"[^a-zA-Z\s]", " ", query)
    query = re.sub(r"\s+", " ", query).strip()

    words = query.split()

    if len(words) > 4:
        query = " ".join(words[:4])

    return query


def get_broad_queries(text: str):
    text_lower = str(text).lower()

    rules = [
        (["fries", "chips", "potato"], ["Potato", "Chips"]),
        (["pasta", "spaghetti", "macaroni", "noodle", "noodles"], ["Pasta", "Spaghetti"]),
        (["salad"], ["Salad"]),
        (["chicken"], ["Chicken"]),
        (["beef", "steak"], ["Beef"]),
        (["pork", "ham", "bacon"], ["Pork"]),
        (["fish", "salmon", "tuna"], ["Fish", "Salmon"]),
        (["shrimp", "prawn", "seafood"], ["Seafood", "Shrimp"]),
        (["egg", "eggs", "omelet", "omelette"], ["Egg"]),
        (["soup", "stew"], ["Soup"]),
        (["rice"], ["Rice"]),
        (["curry"], ["Curry"]),
        (["burger"], ["Burger"]),
        (["sandwich"], ["Sandwich"]),
        (["cake", "dessert", "pie"], ["Cake", "Pie"]),
        (["vegetable", "vegetables", "carrot", "cabbage"], ["Vegetarian", "Vegetable"]),
    ]

    queries = []

    for keywords, broad_values in rules:
        if any(keyword in text_lower for keyword in keywords):
            queries.extend(broad_values)

    return queries


def build_themealdb_queries(query: str):
    queries = []

    original = str(query).strip()
    cleaned = clean_query(original)

    if original:
        queries.append(original)

    if cleaned and cleaned not in queries:
        queries.append(cleaned)

    for broad_query in get_broad_queries(original):
        if broad_query not in queries:
            queries.append(broad_query)

    return queries[:5]


def request_themealdb(query: str):
    if is_themealdb_disabled():
        return []

    cache_key = query.lower().strip()

    if cache_key in THEMEALDB_CACHE:
        return THEMEALDB_CACHE[cache_key]

    try:
        response = requests.get(
            "https://www.themealdb.com/api/json/v1/1/search.php",
            params={"s": query},
            timeout=2
        )

        response.raise_for_status()

        data = response.json()
        meals = data.get("meals") or []

        THEMEALDB_CACHE[cache_key] = meals

        return meals

    except Exception as e:
        print("TheMealDB request error:", e)
        disable_themealdb(seconds=20)
        return []


def build_recipe_text_from_meal(meal: dict) -> str:
    ingredients = []

    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}")

        if ingredient and ingredient.strip():
            ingredients.append(ingredient.strip().lower())

    return f"{meal.get('strMeal', '')} {' '.join(ingredients)}".lower()


def meal_to_recipe(meal: dict):
    recipe_text = build_recipe_text_from_meal(meal)
    calories, protein, fat, carbs = predict_nutrition(recipe_text)

    return {
        "id": str(meal.get("idMeal")),
        "name": meal.get("strMeal"),
        "image": meal.get("strMealThumb"),
        "category": meal.get("strCategory") or "Recipe",
        "area": meal.get("strArea") or "TheMealDB",
        "calories": int(calories),
        "protein": int(protein),
        "fat": int(fat),
        "carbs": int(carbs),
        "has_detail": True,
        "source": "themealdb"
    }


def find_themealdb_recipe_for_candidate(candidate_name: str):
    """
    Ищет реальное блюдо в TheMealDB по названию кандидата из CSV.
    Если ничего не найдено — возвращает None.
    Локальные карточки здесь больше не создаются.
    """

    if not candidate_name:
        return None

    for query in build_themealdb_queries(candidate_name):
        meals = request_themealdb(query)

        if meals:
            return meal_to_recipe(meals[0])

    return None


def search_recipes(query: str, translate: bool = True, limit: int = 12):
    """
    Поиск для Planner.
    Возвращает только реальные рецепты из TheMealDB.
    """

    if not query or not query.strip():
        return []

    search_query = query.strip()

    if translate:
        search_query = translate_query(search_query)

    recipes = []
    seen_ids = set()

    for themealdb_query in build_themealdb_queries(search_query):
        meals = request_themealdb(themealdb_query)

        for meal in meals:
            meal_id = str(meal.get("idMeal"))

            if meal_id in seen_ids:
                continue

            recipes.append(meal_to_recipe(meal))
            seen_ids.add(meal_id)

            if len(recipes) >= limit:
                return recipes

    return recipes


def get_recipes_from_queries(queries, limit=12):
    """
    Универсальная функция для получения реальных рецептов TheMealDB
    по списку простых запросов.
    """

    recipes = []
    seen_ids = set()

    for query in queries:
        if len(recipes) >= limit:
            break

        found = search_recipes(
            query=query,
            translate=False,
            limit=limit
        )

        for recipe in found:
            recipe_id = str(recipe.get("id"))

            if recipe_id in seen_ids:
                continue

            recipes.append(recipe)
            seen_ids.add(recipe_id)

            if len(recipes) >= limit:
                break

    return recipes