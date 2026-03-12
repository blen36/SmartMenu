from pydantic import BaseModel


class ProductResponse(BaseModel):

    id: int
    name: str
    calories: float
    protein: float
    fat: float
    carbs: float
    price: float

    class Config:
        orm_mode = True