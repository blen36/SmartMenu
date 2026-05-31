from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database.db import Base


class RecipeInteraction(Base):
    __tablename__ = "recipe_interactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(String, nullable=False)

    recipe_name = Column(String, nullable=False)

    # 1 = лайк, -1 = дизлайк
    score = Column(Integer, nullable=False)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())