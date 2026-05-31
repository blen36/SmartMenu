from sqlalchemy import Column, Integer, String
from app.database.db import Base


class NutritionCache(Base):

    __tablename__ = "nutrition_cache"

    id = Column(Integer, primary_key=True)

    recipe_id = Column(String, unique=True)

    calories = Column(Integer)
    protein = Column(Integer)
    fat = Column(Integer)
    carbs = Column(Integer)