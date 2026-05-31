import os
import ast
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "data", "recipes_clean.csv")

dataset_ready = False
df = None
vectorizer = None
tfidf_matrix = None


def normalize_ner(value):
    if isinstance(value, list):
        return value

    if not isinstance(value, str):
        return []

    try:
        parsed = ast.literal_eval(value)

        if isinstance(parsed, list):
            return parsed

        return []
    except Exception:
        return []


try:
    df = pd.read_csv(DATASET_PATH)

    df["NER"] = df["NER"].apply(normalize_ner)

    df["combined"] = (
        df["title"].fillna("").astype(str).str.lower()
        + " "
        + df["NER"].apply(lambda items: " ".join([str(x).lower() for x in items]))
    )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=7000,
        ngram_range=(1, 2)
    )

    tfidf_matrix = vectorizer.fit_transform(df["combined"])

    dataset_ready = True

except Exception as e:
    print("Recommendation dataset loading error:", e)
    dataset_ready = False


def profile_to_keywords(profile) -> str:
    if not profile:
        return "chicken vegetables rice salad soup fish"

    goal_keywords = {
        "lose": "salad vegetables chicken fish soup low calorie protein",
        "maintain": "chicken rice vegetables pasta soup fish balanced",
        "gain": "beef chicken rice pasta potatoes cheese eggs protein"
    }

    activity_keywords = {
        "low": "light vegetables soup salad",
        "medium": "balanced chicken fish rice",
        "high": "protein chicken beef rice eggs",
        "very_high": "high protein beef chicken eggs rice pasta"
    }

    return (
        goal_keywords.get(profile.goal, goal_keywords["maintain"])
        + " "
        + activity_keywords.get(profile.activity_level, activity_keywords["medium"])
    )


def get_allergy_terms(profile):
    if not profile or not profile.allergies:
        return []

    return [
        item.strip().lower()
        for item in profile.allergies.split(",")
        if item.strip()
    ]


def contains_allergy(row, allergy_terms):
    if not allergy_terms:
        return False

    text = str(row["combined"]).lower()

    return any(term in text for term in allergy_terms)


def build_candidate_from_row(index, row, score):
    title = str(row["title"]).strip()

    ingredients = row["NER"]

    if isinstance(ingredients, list):
        ingredients_text = ", ".join([str(item) for item in ingredients[:10]])
    else:
        ingredients_text = ""

    return {
        "id": f"local_{int(index)}",
        "name": title,
        "ingredients": ingredients_text,
        "text": str(row["combined"]),
        "content_rank_score": float(score)
    }


def get_recommendation_candidate_rows(
    liked_names=None,
    disliked_names=None,
    profile=None,
    top_n=30
):
    liked_names = liked_names or []
    disliked_names = disliked_names or []

    if not dataset_ready:
        return [
            {
                "id": "local_1",
                "name": "Chicken Salad",
                "ingredients": "chicken, salad, vegetables",
                "text": "chicken salad vegetables",
                "content_rank_score": 0.8
            },
            {
                "id": "local_2",
                "name": "Vegetable Soup",
                "ingredients": "vegetables, soup",
                "text": "vegetable soup",
                "content_rank_score": 0.7
            },
            {
                "id": "local_3",
                "name": "Rice Bowl",
                "ingredients": "rice, chicken, vegetables",
                "text": "rice chicken vegetables",
                "content_rank_score": 0.6
            }
        ][:top_n]

    if liked_names:
        user_text = " ".join(liked_names).lower()
    else:
        user_text = profile_to_keywords(profile)

    user_vector = vectorizer.transform([user_text])
    positive_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()

    final_scores = positive_scores.copy()

    if disliked_names:
        disliked_text = " ".join(disliked_names).lower()
        disliked_vector = vectorizer.transform([disliked_text])
        negative_scores = cosine_similarity(disliked_vector, tfidf_matrix).flatten()

        final_scores = final_scores - 0.35 * negative_scores

    final_scores = final_scores + np.random.uniform(0, 0.02, size=len(final_scores))

    indices = final_scores.argsort()[::-1]

    allergy_terms = get_allergy_terms(profile)

    already_known = set([name.lower() for name in liked_names + disliked_names])

    results = []
    seen_titles = set()

    for index in indices:
        row = df.iloc[index]
        title = str(row["title"]).strip()

        if not title:
            continue

        title_lower = title.lower()

        if title_lower in already_known:
            continue

        if title_lower in seen_titles:
            continue

        if contains_allergy(row, allergy_terms):
            continue

        candidate = build_candidate_from_row(index, row, final_scores[index])

        results.append(candidate)
        seen_titles.add(title_lower)

        if len(results) >= top_n:
            break

    return results


def get_recommendation_candidates(
    liked_names=None,
    disliked_names=None,
    profile=None,
    top_n=30
):
    rows = get_recommendation_candidate_rows(
        liked_names=liked_names,
        disliked_names=disliked_names,
        profile=profile,
        top_n=top_n
    )

    return [item["name"] for item in rows]


def local_search_recipes(query: str, top_n=12):
    """
    Локальный fallback-поиск по recipes_clean.csv.
    Используется, если TheMealDB недоступен или ничего не нашел.
    """

    if not dataset_ready or not query:
        return []

    query_vector = vectorizer.transform([query.lower()])
    scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    indices = scores.argsort()[::-1]

    results = []
    seen_titles = set()

    for index in indices:
        row = df.iloc[index]
        title = str(row["title"]).strip()

        if not title:
            continue

        title_lower = title.lower()

        if title_lower in seen_titles:
            continue

        candidate = build_candidate_from_row(index, row, scores[index])

        results.append(candidate)
        seen_titles.add(title_lower)

        if len(results) >= top_n:
            break

    return results


def get_similar_recipe_names(liked_names, top_n=10):
    return get_recommendation_candidates(
        liked_names=liked_names,
        disliked_names=[],
        profile=None,
        top_n=top_n
    )