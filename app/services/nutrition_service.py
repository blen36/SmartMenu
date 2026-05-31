import os
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "app", "models", "nutrition_model.pkl")

model = None

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        print("Nutrition model loading error:", e)
        model = None


def predict_nutrition(text: str):
    """
    Предсказывает калории, белки, жиры и углеводы по тексту блюда.
    Если модель не найдена, возвращает безопасные средние значения,
    чтобы приложение не падало.
    """

    if not text or len(text.strip()) < 3:
        return 0, 0, 0, 0

    if model is None:
        return 500, 30, 18, 45

    try:
        prediction = model.predict([text])[0]

        calories = max(0, round(float(prediction[0]), 1))
        protein = max(0, round(float(prediction[1]), 1))
        fat = max(0, round(float(prediction[2]), 1))
        carbs = max(0, round(float(prediction[3]), 1))

        return calories, protein, fat, carbs

    except Exception as e:
        print("Nutrition prediction error:", e)
        return 500, 30, 18, 45