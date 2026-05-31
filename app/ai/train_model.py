import os
import joblib
from dotenv import load_dotenv  # <-- ИМПОРТИРУЕМ DOTENV

# ЗАГРУЖАЕМ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ДО ИМПОРТА БАЗЫ!
# Указываем путь к .env файлу в корне проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Только теперь импортируем базу данных
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from app.database.db import SessionLocal
from app.models.interactions import RecipeInteraction

model_path = os.path.join(BASE_DIR, "app", "ai", "recommender_model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "app", "ai", "vectorizer.pkl")


def train_recommender():
    db: Session = SessionLocal()
    interactions = db.query(RecipeInteraction).all()
    db.close()

    if len(interactions) < 5:
        print("Слишком мало данных для обучения. Поставь хотя бы 5 лайков/дизлайков.")
        return

    texts = []
    labels = []

    for i in interactions:
        if i.recipe_name:
            texts.append(i.recipe_name)
            labels.append(1 if i.score == 1 else 0)

    if len(set(labels)) < 2:
        print("Для обучения нужны и лайки, и дизлайки. Поставь хотя бы один дизлайк.")
        return

    print("Обучение модели...")
    vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
    X = vectorizer.fit_transform(texts)
    y = labels

    model = LogisticRegression()
    model.fit(X, y)

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    print("Успех! Файлы recommender_model.pkl и vectorizer.pkl созданы.")


if __name__ == "__main__":
    train_recommender()