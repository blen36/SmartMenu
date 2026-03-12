from pydantic import BaseModel


class RecipeBase(BaseModel):

    name: str
    ingredients: str
    calories: int
    cooking_time: int


class RecipeResponse(RecipeBase):

    id: int

    class Config:
        orm_mode = True