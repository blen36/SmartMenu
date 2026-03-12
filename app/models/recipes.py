from sqlalchemy import Column, Integer, String
from app.database.db import Base


class Recipe(Base):

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    ingredients = Column(String)

    calories = Column(Integer)

    cook_time = Column(Integer)