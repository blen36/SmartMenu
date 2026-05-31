import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

model_path = os.path.join(BASE_DIR, "ai", "recommender_model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "ai", "vectorizer.pkl")


def predict_score(recipe_names):
    if not recipe_names:
        return []

    # Если файлов модели еще нет, возвращаем всем рецептам средний балл (0.5)
    # Это спасает систему от краша (Cold Start)
    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        return [0.5] * len(recipe_names)

    try:
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)

        X = vectorizer.transform(recipe_names)

        # model.predict_proba возвращает вероятности классов (0 - дизлайк, 1 - лайк)
        # Берем вероятность класса "1" (лайк)
        probs = model.predict_proba(X)[:, 1]
        return probs.tolist()
    except Exception as e:
        print(f"Ошибка загрузки модели: {e}")
        return [0.5] * len(recipe_names)