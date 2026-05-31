from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.db import Base


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    day_of_week = Column(String, nullable=False)
    meal_type = Column(String, nullable=False)

    recipe_name = Column(String, nullable=False)
    recipe_id = Column(String, nullable=True)

    calories = Column(Integer, nullable=True)
    protein = Column(Integer, nullable=True)
    fat = Column(Integer, nullable=True)
    carbs = Column(Integer, nullable=True)

    user = relationship("User", back_populates="meal_plans")