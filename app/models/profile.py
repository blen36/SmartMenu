from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.db import Base

class UserProfile(Base):

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    age = Column(Integer)

    height = Column(Integer)

    weight = Column(Integer)

    goal = Column(String)

    allergies = Column(String)