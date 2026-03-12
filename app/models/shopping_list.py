from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.db import Base


class ShoppingList(Base):

    __tablename__ = "shopping_list"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    product_name = Column(String)

    quantity = Column(String)