from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.db import Base


class MealPlan(Base):

    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    day_of_week = Column(String)

    recipe_name = Column(String)