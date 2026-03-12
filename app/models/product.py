from sqlalchemy import Column, Integer, String, Float
from app.database.db import Base


class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    calories = Column(Float)

    protein = Column(Float)

    fat = Column(Float)

    carbs = Column(Float)

    price = Column(Float)