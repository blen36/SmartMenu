from pydantic import BaseModel


class ProfileCreate(BaseModel):

    age: int
    height: int
    weight: int
    goal: str
    allergies: str