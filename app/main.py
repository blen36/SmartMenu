from fastapi import FastAPI
from app.database.db import engine
from app.models import user
from app.routers import users

app = FastAPI()

user.Base.metadata.create_all(bind=engine)

app.include_router(users.router)
@app.get("/")
def home():
    return {"message": "API is working"}