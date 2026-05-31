from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.db import Base


class ViewedRecipe(Base):

    __tablename__="viewed_recipes"

    id=Column(Integer,primary_key=True,index=True)

    user_id=Column(Integer)

    recipe_id=Column(String)

    recipe_name=Column(String)

    recipe_image=Column(String)

    calories=Column(Integer)

    protein=Column(Integer)

    fat=Column(Integer)

    carbs=Column(Integer)

class RecipeRating(Base):
    __tablename__ = "recipe_ratings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer)
    rating = Column(Integer) # 1 для лайка, -1 для дизлайка