from app.models.interactions import RecipeInteraction
from app.models.profile import UserProfile
from app.ai.recommender import get_recommendation_candidate_rows
from app.ai.predictor import predict_score
from app.services.recipe_search_service import (
    find_themealdb_recipe_for_candidate,
    get_recipes_from_queries
)


def nutrition_match_score(recipe: dict, profile: UserProfile) -> float:
    if not profile or not profile.daily_calories:
        return 0.5

    target_calories = profile.daily_calories * 0.30
    target_protein = profile.daily_protein * 0.30
    target_fat = profile.daily_fat * 0.30
    target_carbs = profile.daily_carbs * 0.30

    calories_diff = abs((recipe.get("calories") or 0) - target_calories) / max(target_calories, 1)
    protein_diff = abs((recipe.get("protein") or 0) - target_protein) / max(target_protein, 1)
    fat_diff = abs((recipe.get("fat") or 0) - target_fat) / max(target_fat, 1)
    carbs_diff = abs((recipe.get("carbs") or 0) - target_carbs) / max(target_carbs, 1)

    total_diff = (
        calories_diff * 0.4
        + protein_diff * 0.3
        + fat_diff * 0.15
        + carbs_diff * 0.15
    )

    return max(0.0, 1.0 - total_diff)


def normalize_content_score(value):
    try:
        value = float(value)
    except Exception:
        return 0.5

    if value < 0:
        return 0.0

    if value > 1:
        return 1.0

    return value


def get_fallback_queries(profile, liked_names):
    queries = []

    for name in liked_names[:5]:
        words = str(name).split()

        if words:
            queries.append(words[0])

    if profile:
        if profile.goal == "lose":
            queries.extend(["Salad", "Chicken", "Fish", "Vegetarian", "Soup"])
        elif profile.goal == "gain":
            queries.extend(["Beef", "Chicken", "Pasta", "Rice", "Egg"])
        else:
            queries.extend(["Chicken", "Pasta", "Beef", "Fish", "Rice", "Salad"])
    else:
        queries.extend(["Chicken", "Pasta", "Beef", "Fish", "Rice", "Salad"])

    return queries


def get_recommendations(db, user_id: int, limit: int = 6):
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    interactions = db.query(RecipeInteraction).filter(
        RecipeInteraction.user_id == user_id
    ).all()

    liked = [item.recipe_name for item in interactions if item.score == 1]
    disliked = [item.recipe_name for item in interactions if item.score == -1]
    disliked_lower = set([name.lower() for name in disliked])

    candidates = get_recommendation_candidate_rows(
        liked_names=liked,
        disliked_names=disliked,
        profile=profile,
        top_n=25
    )

    recipes = []
    seen_ids = set()
    seen_names = set()

    # 1. Сначала пробуем найти реальные TheMealDB-рецепты по кандидатам из CSV.
    for candidate in candidates:
        if len(recipes) >= limit:
            break

        recipe = find_themealdb_recipe_for_candidate(candidate.get("name"))

        if not recipe:
            continue

        recipe_id = str(recipe.get("id"))
        recipe_name = str(recipe.get("name", ""))
        recipe_name_lower = recipe_name.lower()

        if recipe_id in seen_ids:
            continue

        if recipe_name_lower in seen_names:
            continue

        if recipe_name_lower in disliked_lower:
            continue

        recipe["content_rank_score"] = normalize_content_score(
            candidate.get("content_rank_score", 0.5)
        )

        recipe["nutrition_score"] = nutrition_match_score(recipe, profile)

        recipes.append(recipe)
        seen_ids.add(recipe_id)
        seen_names.add(recipe_name_lower)

    # 2. Если реальных рецептов не хватило, добираем реальными TheMealDB-рецептами
    # по широким запросам, связанным с целью пользователя.
    if len(recipes) < limit:
        fallback_queries = get_fallback_queries(profile, liked)

        fallback_recipes = get_recipes_from_queries(
            queries=fallback_queries,
            limit=limit * 2
        )

        for recipe in fallback_recipes:
            if len(recipes) >= limit:
                break

            recipe_id = str(recipe.get("id"))
            recipe_name = str(recipe.get("name", ""))
            recipe_name_lower = recipe_name.lower()

            if recipe_id in seen_ids:
                continue

            if recipe_name_lower in seen_names:
                continue

            if recipe_name_lower in disliked_lower:
                continue

            recipe["content_rank_score"] = 0.45
            recipe["nutrition_score"] = nutrition_match_score(recipe, profile)

            recipes.append(recipe)
            seen_ids.add(recipe_id)
            seen_names.add(recipe_name_lower)

    names = [recipe["name"] for recipe in recipes]
    ml_scores = predict_score(names)

    scored_recipes = []

    for recipe, ml_score in zip(recipes, ml_scores):
        final_score = (
            recipe.get("content_rank_score", 0.5) * 0.45
            + recipe.get("nutrition_score", 0.5) * 0.30
            + float(ml_score) * 0.25
        )

        recipe["score"] = round(final_score, 4)
        scored_recipes.append(recipe)

    scored_recipes.sort(key=lambda item: item["score"], reverse=True)

    return scored_recipes[:limit]