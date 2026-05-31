from app.services.recipe_search_service import get_recipes_from_queries


days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

meals = [
    ("Breakfast", 0.25),
    ("Lunch", 0.40),
    ("Dinner", 0.35)
]


def get_menu_queries(profile):
    if profile.goal == "lose":
        return [
            "Egg",
            "Salad",
            "Chicken",
            "Fish",
            "Vegetarian",
            "Soup",
            "Rice"
        ]

    if profile.goal == "gain":
        return [
            "Egg",
            "Beef",
            "Chicken",
            "Pasta",
            "Rice",
            "Pork",
            "Curry"
        ]

    return [
        "Egg",
        "Chicken",
        "Pasta",
        "Beef",
        "Fish",
        "Rice",
        "Vegetarian",
        "Soup"
    ]


def meal_score(recipe, target_calories, target_protein, target_fat, target_carbs):
    return (
        abs((recipe.get("calories") or 0) - target_calories)
        + abs((recipe.get("protein") or 0) - target_protein) * 3
        + abs((recipe.get("fat") or 0) - target_fat) * 2
        + abs((recipe.get("carbs") or 0) - target_carbs)
    )


def pick_best_recipe(pool, used_ids, target_calories, target_protein, target_fat, target_carbs):
    available = [
        recipe for recipe in pool
        if str(recipe.get("id")) not in used_ids
    ]

    if not available:
        available = pool

    if not available:
        return None

    best_recipe = min(
        available,
        key=lambda recipe: meal_score(
            recipe,
            target_calories,
            target_protein,
            target_fat,
            target_carbs
        )
    )

    return best_recipe


def generate_menu_for_user(profile):
    queries = get_menu_queries(profile)

    # Берем реальный пул блюд из TheMealDB.
    # Если API работает, обычно этого хватает на 21 блюдо.
    pool = get_recipes_from_queries(
        queries=queries,
        limit=40
    )

    if not pool:
        return []

    targets = {
        "calories": profile.daily_calories or 2000,
        "protein": profile.daily_protein or 120,
        "fat": profile.daily_fat or 70,
        "carbs": profile.daily_carbs or 220
    }

    menu = []
    used_ids = set()

    for day in days:
        for meal_name, ratio in meals:
            target_calories = targets["calories"] * ratio
            target_protein = targets["protein"] * ratio
            target_fat = targets["fat"] * ratio
            target_carbs = targets["carbs"] * ratio

            recipe = pick_best_recipe(
                pool=pool,
                used_ids=used_ids,
                target_calories=target_calories,
                target_protein=target_protein,
                target_fat=target_fat,
                target_carbs=target_carbs
            )

            if not recipe:
                continue

            used_ids.add(str(recipe.get("id")))

            menu.append({
                "day": day,
                "meal": meal_name,
                "name": recipe["name"],
                "recipe_id": recipe["id"],
                "calories": int(recipe.get("calories") or 0),
                "protein": int(recipe.get("protein") or 0),
                "fat": int(recipe.get("fat") or 0),
                "carbs": int(recipe.get("carbs") or 0)
            })

    return menu