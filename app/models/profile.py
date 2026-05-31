from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
import enum

from app.database.db import Base


class Gender(str, enum.Enum):
    male = "male"
    female = "female"


class ActivityLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    very_high = "very_high"


class Goal(str, enum.Enum):
    lose = "lose"
    maintain = "maintain"
    gain = "gain"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    age = Column(Integer, nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)

    gender = Column(String, nullable=False)
    activity_level = Column(String, nullable=False)
    goal = Column(String, nullable=False)

    allergies = Column(String, nullable=True)

    daily_calories = Column(Float, nullable=True)
    daily_protein = Column(Float, nullable=True)
    daily_fat = Column(Float, nullable=True)
    daily_carbs = Column(Float, nullable=True)

    user = relationship("User", back_populates="profile")